"""Elasticsearch manager for trigger execution history.

This module handles CRUD operations for trigger execution history,
including querying with filters and cleanup of old records.
"""
from datetime import datetime, timedelta
from typing import List, Optional

from elasticsearch import Elasticsearch
from loguru import logger

from core.model.trigger import TriggerExecutionStatus


class ElasticsearchTriggerHistoryManager:
    """Manages trigger execution history in Elasticsearch.

    Provides CRUD operations for storing and querying trigger execution
    history with support for filtering and pagination.
    """

    TRIGGER_HISTORY_INDEX = "knowledge_trigger_history"

    def __init__(self, es_client: Elasticsearch):
        """Initialize trigger history manager.

        Args:
            es_client: Elasticsearch client instance
        """
        self.es_client = es_client

    def add_execution(self, execution: TriggerExecutionStatus) -> bool:
        """Add a trigger execution record to history.

        Args:
            execution: Execution status to record

        Returns:
            True if successfully added, False otherwise
        """
        try:
            # Convert execution to dict
            doc = execution.model_dump()

            # Format datetime for ES
            if isinstance(doc.get("executed_at"), datetime):
                doc["executed_at"] = doc["executed_at"].strftime("%Y-%m-%d %H:%M:%S")

            # Index the document
            response = self.es_client.index(
                index=self.TRIGGER_HISTORY_INDEX,
                id=execution.execution_id,
                body=doc,
                refresh=True  # Make immediately searchable
            )

            logger.debug(
                f"Added execution history: execution_id={execution.execution_id}, "
                f"trigger_id={execution.trigger_id}, status={execution.status}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to add execution history: {str(e)}")
            return False

    def get_execution_by_id(self, execution_id: str) -> Optional[dict]:
        """Get execution record by ID.

        Args:
            execution_id: Execution ID

        Returns:
            Execution record dict or None if not found
        """
        try:
            response = self.es_client.get(
                index=self.TRIGGER_HISTORY_INDEX,
                id=execution_id
            )

            return response.get("_source")

        except Exception as e:
            logger.warning(f"Failed to get execution by ID: execution_id={execution_id}, error={str(e)}")
            return None

    def query_executions(
        self,
        kb_name: Optional[str] = None,
        trigger_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """Query execution history with filters and pagination.

        Args:
            kb_name: Filter by knowledge base name
            trigger_id: Filter by trigger ID
            status: Filter by execution status
            start_date: Filter by start date (inclusive)
            end_date: Filter by end date (inclusive)
            page: Page number (1-based)
            page_size: Records per page

        Returns:
            Dictionary with 'total', 'page', 'page_size', 'records' keys
        """
        try:
            # Build query clauses
            must_clauses = []

            if kb_name:
                must_clauses.append({"term": {"kb_name": kb_name}})

            if trigger_id:
                must_clauses.append({"term": {"trigger_id": trigger_id}})

            if status:
                must_clauses.append({"term": {"status": status}})

            # Date range filter
            if start_date or end_date:
                range_clause = {}
                if start_date:
                    range_clause["gte"] = start_date.strftime("%Y-%m-%d %H:%M:%S")
                if end_date:
                    range_clause["lte"] = end_date.strftime("%Y-%m-%d %H:%M:%S")

                if range_clause:
                    must_clauses.append({"range": {"executed_at": range_clause}})

            # Build query
            query = {"match_all": {}} if not must_clauses else {"bool": {"must": must_clauses}}

            # Execute search with pagination
            from_index = (page - 1) * page_size
            response = self.es_client.search(
                index=self.TRIGGER_HISTORY_INDEX,
                body={
                    "query": query,
                    "from": from_index,
                    "size": page_size,
                    "sort": [{"executed_at": {"order": "desc"}}]  # Most recent first
                }
            )

            # Extract results
            hits = response.get("hits", {})
            total = hits.get("total", {}).get("value", 0)
            records = [hit.get("_source") for hit in hits.get("hits", [])]

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "records": records
            }

        except Exception as e:
            logger.error(f"Failed to query executions: {str(e)}")
            return {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "records": []
            }

    def delete_old_executions(self, retention_days: int) -> int:
        """Delete execution records older than retention period.

        Args:
            retention_days: Number of days to retain records

        Returns:
            Number of deleted records
        """
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")

            # Delete by query
            response = self.es_client.delete_by_query(
                index=self.TRIGGER_HISTORY_INDEX,
                body={
                    "query": {
                        "range": {
                            "executed_at": {
                                "lt": cutoff_str
                            }
                        }
                    }
                }
            )

            deleted_count = response.get("deleted", 0)
            logger.info(
                f"Deleted old execution records: count={deleted_count}, "
                f"retention_days={retention_days}"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete old executions: {str(e)}")
            return 0

    def get_execution_stats(
        self,
        kb_name: Optional[str] = None,
        trigger_id: Optional[str] = None
    ) -> dict:
        """Get execution statistics for monitoring.

        Args:
            kb_name: Filter by knowledge base name (optional)
            trigger_id: Filter by trigger ID (optional)

        Returns:
            Dictionary with statistics (total_count, success_rate, etc.)
        """
        try:
            # Build query
            must_clauses = []
            if kb_name:
                must_clauses.append({"term": {"kb_name": kb_name}})
            if trigger_id:
                must_clauses.append({"term": {"trigger_id": trigger_id}})

            query = {"match_all": {}} if not must_clauses else {"bool": {"must": must_clauses}}

            # Aggregate by status
            response = self.es_client.search(
                index=self.TRIGGER_HISTORY_INDEX,
                body={
                    "query": query,
                    "size": 0,  # Don't return documents
                    "aggs": {
                        "status_counts": {
                            "terms": {
                                "field": "status",
                                "size": 10
                            }
                        },
                        "total_executions": {
                            "value_count": {
                                "field": "_id"
                            }
                        }
                    }
                }
            )

            # Extract aggregations
            aggs = response.get("aggregations", {})
            status_buckets = aggs.get("status_counts", {}).get("buckets", [])
            total = aggs.get("total_executions", {}).get("value", 0)

            # Calculate success rate
            success_count = 0
            status_counts = {}
            for bucket in status_buckets:
                status = bucket.get("key")
                count = bucket.get("doc_count", 0)
                status_counts[status] = count
                if status == "success":
                    success_count = count

            success_rate = (success_count / total * 100) if total > 0 else 0

            return {
                "total_executions": total,
                "success_count": success_count,
                "success_rate": round(success_rate, 2),
                "status_breakdown": status_counts
            }

        except Exception as e:
            logger.error(f"Failed to get execution stats: {str(e)}")
            return {
                "total_executions": 0,
                "success_count": 0,
                "success_rate": 0,
                "status_breakdown": {}
            }
