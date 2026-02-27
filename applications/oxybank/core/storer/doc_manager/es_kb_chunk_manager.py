import uuid
from datetime import datetime
from typing import List, Sequence, Dict, Any

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from llama_index.core.schema import BaseNode
from loguru import logger


class ElasticsearchKbChunkManager:

    def __init__(
            self,
            es_client: Elasticsearch,
            index_name: str = 'knowledge_chunk_info'
    ):
        self.client = es_client
        self.index_name = index_name

        # Check connection
        try:
            if not self.client.ping():
                raise ConnectionError("Elasticsearch client error")
        except Exception as e:
            raise ConnectionError(f"Elasticsearch client error: {str(e)}")

    def kb_delete_chunk(self, kb_id: str, group_ids: List[str]) -> bool:
        """
        Delete corresponding chunk information based on knowledge base ID and group ID list

        Args:
            kb_id: Knowledge base ID
            group_ids: List of group IDs to delete (sys_group field values)

        Returns:
            bool: Whether deletion was successful
        """
        try:
            if not group_ids:
                logger.info("No group IDs to delete")
                return True
            if not self.client.indices.exists(index=self.index_name):
                logger.info(f"Index {self.index_name} does not exist, no need to delete chunk data")
                return True

            # Build delete query: match both kb_id and sys_group
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"kb_id": kb_id}},
                            {"terms": {"sys_group": group_ids}}
                        ]
                    }
                }
            }

            # Execute delete operation
            response = self.client.delete_by_query(
                index=self.index_name,
                body=query,
                refresh=True  # Refresh immediately to make deletion effective
            )

            deleted_count = response.get("deleted", 0)
            logger.info(f"Successfully deleted {deleted_count} chunk records (kb_id: {kb_id}, group_ids: {group_ids})")

            return True

        except NotFoundError:
            logger.info(f"Index {self.index_name} does not exist, no need to delete chunk data")
            return True
        except Exception as e:
            logger.error(f"Failed to delete chunk records (kb_id: {kb_id}, group_ids: {group_ids}): {str(e)}")
            return False

    def kb_add_chunk(self, nodes: Sequence[BaseNode]) -> bool:
        """
        Batch write LlamaIndex Document objects to ES index

        Args:
            nodes: Sequence of LlamaIndex Document objects

        Returns:
            bool: Whether write was successful
        """
        try:
            if not nodes:
                logger.info("No chunk data to add")
                return True

            # Prepare batch operation data
            bulk_body = []
            current_time = datetime.now().isoformat()
            successful_count = 0

            for node in nodes:
                # Get Document metadata
                metadata = node.metadata or {}

                # Map to ES index fields with new system field names
                es_doc = {
                    # RAG related fields
                    "kb_id": metadata.get('kb_id', ''),
                    "sys_sample_id": metadata.get('sys_sample_id', f"sample_{uuid.uuid4().hex[:16]}"),
                    "sys_group": metadata.get('sys_group', ''),
                    "chunk_text": node.text,
                    "chunk_extra_data": {},
                    "language": ""
                }

                # Add to batch operation
                # Batch operation format: index operation + document content
                bulk_body.append({
                    "index": {
                        "_index": self.index_name
                    }
                })
                bulk_body.append(es_doc)
                successful_count += 1

            # Execute batch insert
            if bulk_body:
                response = self.client.bulk(
                    body=bulk_body,
                    refresh=True  # Refresh immediately to make data searchable
                )

                # Check batch operation results
                if response.get("errors", False):
                    # Handle errors
                    error_count = 0
                    for item in response["items"]:
                        if "index" in item and item["index"].get("status", 200) >= 400:
                            error_count += 1
                            logger.error(f"Insert failed: {item['index'].get('error', {})}")

                    logger.warning(f"Partial insert failed: success {successful_count - error_count}, failed {error_count}")
                    return False if error_count == successful_count else True
                else:
                    logger.info(f"Successfully inserted {successful_count} chunks to ES index {self.index_name}")
                    return True
        except Exception as e:
            logger.error(f"Batch insert chunks failed: {str(e)}")
            return False

    def get_kb_chunks(
            self,
            kb_id: str,
            page: int = 1,
            size: int = 10
    ) -> Dict[str, Any]:
        try:
            # Calculate from value (starts from 0)
            from_value = (page - 1) * size

            resp = self.client.search(
                index=self.index_name,
                body={
                    "query": {
                        "term": {
                            "kb_id": kb_id
                        }
                    },
                    "from": from_value,
                    "size": size
                }
            )
            hits = resp['hits']['hits']
            total = resp['hits']['total']['value']
            result = [doc["_source"] for doc in hits]
            return {
                "items": result,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        except Exception as e:
            logger.error(f"search knowledge chunks of [{kb_id}] error: {e}")
            return {
                "items": [],
                "total": 0,
                "page": page,
                "size": size,
                "pages": 0
            }

    def get_kb_file_chunks(
            self,
            kb_id: str,
            group_id: str,
            page: int = 1,
            size: int = 10
    ) -> Dict[str, Any]:
        try:
            # Calculate from value (starts from 0)
            from_value = (page - 1) * size

            resp = self.client.search(
                index=self.index_name,
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"kb_id": kb_id}},
                                {"term": {"sys_group": group_id}}
                            ]
                        },
                    "from": from_value,
                    "size": size
                    }
                }
            )
            hits = resp['hits']['hits']
            total = resp['hits']['total']['value']
            result = [doc["_source"] for doc in hits]
            return {
                "items": result,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        except Exception as e:
            logger.error(f"search knowledge chunks of [kb_id:{kb_id}] [group_id:{group_id}] error: {e}")
            return {
                "items": [],
                "total": 0,
                "page": page,
                "size": size,
                "pages": 0
            }
