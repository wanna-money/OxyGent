"""Condition detector for trigger system.

This module handles Elasticsearch query logic for detecting records that match
trigger conditions, with deduplication support.
"""
from typing import Any, Dict, List

from elasticsearch import Elasticsearch
from loguru import logger

from core.model.trigger import TriggerCondition, TriggerConfig


class TriggerDetector:
    """Detects knowledge base records that match trigger conditions.

    Queries Elasticsearch to find records matching trigger conditions,
    with support for:
    - Multiple condition combinations (AND logic)
    - Various comparison operators (eq, ne, contains, startswith, endswith)
    - Deduplication based on trigger_execution_log field
    """

    def __init__(self, es_client: Elasticsearch):
        """Initialize trigger detector.

        Args:
            es_client: Elasticsearch client instance
        """
        self.es_client = es_client

    def detect_matching_records(
        self,
        trigger: TriggerConfig,
        kb_id: str,
        kb_name: str,
        index_name: str,
        size: int = 100
    ) -> List[Dict[str, Any]]:
        """Detect records matching trigger conditions.

        Args:
            trigger: Trigger configuration with conditions
            kb_id: Knowledge base ID
            kb_name: Knowledge base name
            index_name: Elasticsearch index name for the KB
            size: Maximum number of records to return

        Returns:
            List of matching records (empty list if no matches)
        """
        try:
            # Build ES query from trigger conditions
            query = self._build_trigger_query(trigger, kb_id, index_name)

            logger.debug(
                f"Detecting records for trigger: trigger_id={trigger.trigger_id}, "
                f"kb_name={kb_name}, conditions={len(trigger.conditions)}"
            )

            # Execute ES query
            response = self.es_client.search(
                index=index_name,
                body={"query": query, "size": size},
                _source=True  # Return full document
            )

            hits = response.get("hits", {}).get("hits", [])
            records = [hit["_source"] for hit in hits]

            logger.info(
                f"Detected {len(records)} matching records: trigger_id={trigger.trigger_id}, "
                f"kb_name={kb_name}"
            )

            return records

        except Exception as e:
            logger.error(
                f"Failed to detect matching records: trigger_id={trigger.trigger_id}, "
                f"kb_name={kb_name}, error={str(e)}"
            )
            return []

    def _build_trigger_query(self, trigger: TriggerConfig, kb_id: str, index_name: str) -> Dict[str, Any]:
        """Build Elasticsearch query from trigger conditions.

        Constructs a bool query with:
        - must: All trigger conditions (AND logic)
        - must_not: Deduplication (exclude recently triggered records)

        Args:
            trigger: Trigger configuration
            kb_id: Knowledge base ID to filter by
            index_name: Elasticsearch index name for mapping lookup

        Returns:
            Elasticsearch query dict
        """
        must_clauses = [
            {"term": {"kb_id": kb_id}}  # Always filter by KB ID
        ]

        # Build condition clauses
        for condition in trigger.conditions:
            must_clauses.append(
                self._build_condition_clause(condition, index_name)
            )

        # Build deduplication clause
        must_not_clauses = [
            self._build_deduplication_clause(trigger.trigger_id)
        ]

        query = {
            "bool": {
                "must": must_clauses,
                "must_not": must_not_clauses
            }
        }

        return query

    def _get_query_field_name(self, field_name: str, index_name: str) -> str:
        """Get the correct field name for ES queries based on mapping.

        For string fields, ES mappings can be:
        1. Pure keyword type: use field_name directly
        2. Text with keyword subfield: use field_name.keyword
        3. Pure text type: use field_name directly

        Args:
            field_name: Original field name
            index_name: Elasticsearch index name

        Returns:
            Field name to use in query (e.g., "field" or "field.keyword")
        """
        try:
            # Get index mapping
            mapping = self.es_client.indices.get_mapping(index=index_name)
            properties = mapping[index_name]['mappings']['properties']

            # Check if field exists in mapping
            if field_name not in properties:
                # Field doesn't exist in mapping, use as-is
                logger.warning(f"Field {field_name} not found in mapping, using as-is")
                return field_name

            field_mapping = properties[field_name]
            field_type = field_mapping.get('type')

            # If it's a pure keyword field, use field name directly
            if field_type == 'keyword':
                return field_name

            # If it's a text field, check for keyword subfield
            if field_type == 'text':
                fields = field_mapping.get('fields', {})
                if 'keyword' in fields:
                    # Has keyword subfield, use it for exact matching
                    return f"{field_name}.keyword"
                else:
                    # No keyword subfield, use field name directly
                    return field_name

            # For other types (integer, float, etc.), use field name directly
            return field_name

        except Exception as e:
            logger.warning(
                f"Failed to get mapping for field {field_name} in index {index_name}, "
                f"using default behavior: {str(e)}"
            )
            # Fallback: assume keyword subfield exists
            return f"{field_name}.keyword"

    def _build_condition_clause(self, condition: TriggerCondition, index_name: str) -> Dict[str, Any]:
        """Build Elasticsearch query clause for a single condition.

        Args:
            condition: Trigger condition
            index_name: Elasticsearch index name for mapping lookup

        Returns:
            Elasticsearch query clause

        Raises:
            ValueError: If operator is not supported
        """
        field_name = condition.field_name
        field_value = condition.field_value
        operator = condition.operator

        # Get the correct field name based on ES mapping
        query_field = self._get_query_field_name(field_name, index_name)

        # Handle different operators
        if operator == "eq":
            return {"term": {query_field: field_value}}

        elif operator == "ne":
            return {"bool": {"must_not": [{"term": {query_field: field_value}}]}}

        elif operator == "contains":
            return {"wildcard": {query_field: f"*{field_value}*"}}

        elif operator == "startswith":
            return {"prefix": {query_field: field_value}}

        elif operator == "endswith":
            return {"wildcard": {query_field: f"*{field_value}"}}

        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def _build_deduplication_clause(self, trigger_id: str) -> Dict[str, Any]:
        """Build deduplication clause to exclude recently triggered records.

        Prevents re-triggering records that were recently processed by this trigger
        using the trigger_execution_log field.

        Args:
            trigger_id: Trigger ID to check against

        Returns:
            Elasticsearch range query clause
        """
        # Exclude records triggered in the last 10 minutes
        # This allows for some retry window but prevents rapid re-triggering
        return {
            "range": {
                f"trigger_execution_log.{trigger_id}": {
                    "gte": "now-10m"  # Elasticsearch date math
                }
            }
        }

    def update_trigger_execution_log(
        self,
        index_name: str,
        sample_ids: List[str],
        trigger_id: str
    ) -> bool:
        """Update trigger_execution_log field for processed records.

        Marks records as processed by this trigger to prevent re-triggering.

        Args:
            index_name: Elasticsearch index name
            sample_ids: List of sample IDs (sys_sample_id values)
            trigger_id: Trigger ID

        Returns:
            True if update succeeded, False otherwise
        """
        if not sample_ids:
            return True

        try:
            # Build bulk update payload
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            # First, query to get real ES document IDs for all sample_ids
            # Include sys_sample_id in _source to build mapping
            search_response = self.es_client.search(
                index=index_name,
                body={
                    "query": {
                        "terms": {"sys_sample_id": sample_ids}
                    },
                    "_source": ["sys_sample_id"],  # Only return sys_sample_id field
                    "size": len(sample_ids)
                }
            )

            # Map sys_sample_id to real ES _id
            sample_id_to_doc_id = {}
            for hit in search_response.get('hits', {}).get('hits', []):
                sys_sample_id = hit.get('_source', {}).get('sys_sample_id')
                if sys_sample_id:
                    sample_id_to_doc_id[sys_sample_id] = hit['_id']

            # Build bulk update payload using real ES document IDs
            bulk_body = []
            for sample_id in sample_ids:
                # Skip if sample_id not found in ES
                if sample_id not in sample_id_to_doc_id:
                    logger.warning(f"Sample ID not found in ES: {sample_id}, skipping trigger_execution_log update")
                    continue

                real_doc_id = sample_id_to_doc_id[sample_id]

                # Update operation using real ES document ID
                bulk_body.append({
                    "update": {
                        "_index": index_name,
                        "_id": real_doc_id  # Use real ES document ID
                    }
                })
                # Update document with trigger execution timestamp
                bulk_body.append({
                    "doc": {
                        "trigger_execution_log": {
                            trigger_id: timestamp
                        }
                    }
                })

            if not bulk_body:
                logger.warning("No valid documents to update trigger_execution_log")
                return False

            # Execute bulk update
            response = self.es_client.bulk(body=bulk_body)

            if response.get("errors"):
                logger.warning(
                    f"Bulk update had errors: trigger_id={trigger_id}, "
                    f"sample_ids={len(sample_ids)}, response={response}"
                )
                return False

            logger.debug(
                f"Updated trigger_execution_log: trigger_id={trigger_id}, "
                f"sample_ids={len(sample_ids)}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to update trigger_execution_log: trigger_id={trigger_id}, "
                f"error={str(e)}"
            )
            return False

    def bulk_update_records(
        self,
        index_name: str,
        updated_records: List[dict],
        kb_id: str,
        kb_name: str
    ) -> bool:
        """Bulk update ES records using deposit logic (same as ingest_kb_data endpoint).

        This method directly replicates the deposit logic from knowledge_file.py:ingest_kb_data,
        but for updating existing records instead of inserting new ones.

        Args:
            index_name: Elasticsearch index name (same as kb_name)
            updated_records: List of updated records from HTTP response
            kb_id: Knowledge base ID
            kb_name: Knowledge base name

        Returns:
            True if update succeeded, False otherwise
        """
        if not updated_records:
            return True

        try:
            from datetime import datetime
            import pandas as pd
            from core.config import settings
            from core.storer.doc_manager.es_kb_base_manager import ElasticsearchKbBaseManager
            from core.storer.doc_manager.es_kb_file_manager import ElasticsearchKbFileManager
            from core.storer.doc_manager.knowledge_index import KBSchema, check_kb_schema, VearchVectorMatchPolicy
            from core.storer.doc_manager.schema_utils import convert_dataframe_types_by_schema
            from core.storer.vector_manager.vearch_manager import VearchManager

            # 1. Get KB Schema
            kb_base_client = ElasticsearchKbBaseManager(self.es_client)
            kb_schema_dict = kb_base_client.get_kb_schema_by_id(kb_id)
            if not kb_schema_dict:
                logger.error(f"kb_id: [{kb_id}] has no KB schema")
                return False

            # 2. Parse and validate KB Schema
            try:
                kb_schema = KBSchema(**kb_schema_dict)
                if not check_kb_schema(kb_schema):
                    logger.error("KB schema validation failed")
                    return False
            except Exception as e:
                logger.error(f"Failed to parse kb_schema: {e}")
                return False

            # 3. Convert to DataFrame
            try:
                df = pd.DataFrame(updated_records)
            except ValueError:
                df = pd.DataFrame(updated_records)

            # 4. Convert types according to schema
            df = convert_dataframe_types_by_schema(df, kb_schema)

            # 5. Add update timestamp (use sys_update_time to match Vearch space schema)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df['sys_update_time'] = current_time

            # 6. Update ES documents (using ES update instead of insert)
            kb_file_client = ElasticsearchKbFileManager(self.es_client)
            updated_count = 0
            failed_count = 0

            for idx, row in df.iterrows():
                sys_sample_id = row.get('sys_sample_id')
                if not sys_sample_id:
                    logger.warning(f"Record missing sys_sample_id: {row.to_dict()}")
                    failed_count += 1
                    continue

                # Query ES to get real document _id by sys_sample_id
                try:
                    search_response = self.es_client.search(
                        index=index_name,
                        body={
                            "query": {
                                "term": {"sys_sample_id": sys_sample_id}
                            },
                            "_source": False,  # Only return _id, not _source
                            "size": 1
                        }
                    )

                    hits = search_response.get('hits', {}).get('hits', [])
                    if not hits:
                        logger.error(f"Document not found for sys_sample_id={sys_sample_id}")
                        failed_count += 1
                        continue

                    real_doc_id = hits[0]['_id']

                except Exception as e:
                    logger.error(f"Failed to query document for sys_sample_id={sys_sample_id}: {e}")
                    failed_count += 1
                    continue

                # Build update document
                update_doc = row.to_dict()
                # Remove internal fields that shouldn't be in update
                update_doc.pop('_id', None)

                # Update ES document using real _id
                try:
                    self.es_client.update(
                        index=index_name,
                        id=real_doc_id,
                        body={"doc": update_doc}
                    )
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Failed to update document real_id={real_doc_id}, sys_sample_id={sys_sample_id}: {e}")
                    failed_count += 1

            logger.info(f"ES update complete: updated={updated_count}, failed={failed_count}")

            # 7. Check if vector fields need regeneration
            if kb_schema.match_rules:
                # Collect vector match policies
                vec_matches = [
                    policy
                    for match_rule in kb_schema.match_rules
                    for policy in match_rule.match_policies
                    if isinstance(policy, VearchVectorMatchPolicy)
                ]

                if vec_matches:
                    # Check if any vector fields were in the updated records
                    vec_field_names = {policy.input_fields[0] for policy in vec_matches}
                    updated_vec_fields = vec_field_names & set(df.columns)

                    if updated_vec_fields:
                        logger.info(f"Vector fields updated: {updated_vec_fields}, regenerating embeddings...")

                        # Generate embeddings for updated vector fields
                        embed_model = settings.embedding_model
                        vearch_manager = VearchManager(vearch_client=settings.vearch_client)

                        for field_name in updated_vec_fields:
                            if field_name not in df.columns:
                                continue

                            # Generate embeddings
                            texts = df[field_name].astype(str).tolist()
                            embeddings = embed_model.get_text_embedding_batch(texts, show_progress=False)

                            vector_field_name = f"{field_name}_vector"
                            df[vector_field_name] = embeddings

                            logger.info(f"Regenerated {len(embeddings)} embeddings for field {field_name}")

                        # Filter DataFrame to only include fields in Vearch space schema
                        # Vearch space schema includes:
                        # 1. User-defined fields from kb_schema
                        # 2. Vector fields ({field_name}_vector)
                        # 3. System fields (sys_*)
                        allowed_vearch_fields = set()

                        # Add user-defined fields
                        for field in kb_schema.fields:
                            allowed_vearch_fields.add(field.field_name)

                        # Add vector fields
                        for field_name in vec_field_names:
                            allowed_vearch_fields.add(f"{field_name}_vector")

                        # Add system fields (defined in knowledge_index.py:CHUNK_SYSTEM_FIELDS)
                        system_fields = [
                            "kb_id", "sys_sample_id", "sys_group", "sys_template",
                            "sys_priority", "sys_status", "sys_executor", "sys_overview",
                            "sys_remarks", "sys_create_time", "sys_update_time"
                        ]
                        allowed_vearch_fields.update(system_fields)

                        # Filter DataFrame columns
                        existing_allowed_fields = [col for col in df.columns if col in allowed_vearch_fields]
                        df_vearch = df[existing_allowed_fields].copy()

                        logger.debug(
                            f"Filtered DataFrame for Vearch: {len(df.columns)} -> {len(df_vearch.columns)} columns, "
                            f"removed: {set(df.columns) - set(existing_allowed_fields)}"
                        )

                        # Update Vearch (using upsert which handles both insert and update)
                        try:
                            vearch_add_result = vearch_manager.add_df(
                                database_name=settings.vearch_config.db_name,
                                space_name=kb_name,
                                df=df_vearch
                            )

                            if not vearch_add_result:
                                logger.warning(f"Failed to update Vearch space: {kb_name}")
                            else:
                                logger.info(f"Vearch update successful: space={kb_name}")
                        except Exception as e:
                            logger.error(f"Vearch update failed: {e}")
                            # Don't fail the operation if Vearch update fails

            logger.info(
                f"Deposit logic completed: kb_name={kb_name}, "
                f"updated={updated_count}, failed={failed_count}"
            )
            return failed_count == 0

        except Exception as e:
            logger.error(
                f"Failed to bulk update records using deposit logic: "
                f"kb_name={kb_name}, error={str(e)}"
            )
            return False
