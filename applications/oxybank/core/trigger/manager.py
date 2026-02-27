"""Trigger manager for orchestrating trigger detection and execution.

This module manages the polling loop that detects and executes triggers
for all knowledge bases at regular intervals.
"""
from typing import List

from loguru import logger

from core.config import settings
from core.model.trigger import TriggerConfig, TriggerExecutionStatus
from core.storer.doc_manager.es_kb_base_manager import ElasticsearchKbBaseManager
from core.storer.doc_manager.trigger_history_manager import ElasticsearchTriggerHistoryManager
from core.trigger.detector import TriggerDetector
from core.trigger.executor import TriggerExecutor


class TriggerManager:
    """Manages trigger detection and execution for all knowledge bases.

    Orchestrates the polling loop that:
    1. Fetches all knowledge bases with enabled triggers
    2. Detects matching records for each trigger
    3. Executes HTTP callbacks
    4. Records execution history
    """

    def __init__(
        self,
        kb_manager: ElasticsearchKbBaseManager | None = None,
        history_manager: ElasticsearchTriggerHistoryManager | None = None,
        detector: TriggerDetector | None = None,
        executor: TriggerExecutor | None = None
    ):
        """Initialize trigger manager.

        Args:
            kb_manager: Knowledge base manager (optional, will create default)
            history_manager: Trigger history manager (optional, will create default)
            detector: Trigger detector (optional, will create default)
            executor: Trigger executor (optional, will create default)
        """
        from core.config import settings

        # Initialize components
        self.kb_manager = kb_manager or ElasticsearchKbBaseManager(settings.es_client)
        self.history_manager = history_manager or ElasticsearchTriggerHistoryManager(settings.es_client)
        self.detector = detector or TriggerDetector(settings.es_client)
        self.executor = executor or TriggerExecutor()

        self.is_running = False

    async def detect_and_trigger(self) -> None:
        """Main detection loop entry point.

        Called by APScheduler at regular intervals to:
        1. Fetch all KBs with enabled triggers
        2. For each trigger, detect matching records
        3. Execute callbacks and record history

        This method is designed to be called by the scheduler.
        """
        if self.is_running:
            logger.warning("Trigger detection already in progress, skipping this cycle")
            return

        self.is_running = True
        try:
            await self._process_all_triggers()
        except Exception as e:
            logger.error(f"Trigger detection loop failed: {str(e)}", exc_info=True)
        finally:
            self.is_running = False

    async def _process_all_triggers(self) -> None:
        """Process all triggers across all knowledge bases.

        Fetches all knowledge bases, extracts their trigger configurations,
        and processes each enabled trigger.
        """
        logger.debug("Starting trigger detection cycle")

        # Fetch all knowledge bases
        all_kbs = self.kb_manager.kb_list_all()
        if not all_kbs:
            logger.debug("No knowledge bases found")
            return

        # Collect all enabled triggers from all KBs
        all_triggers = []
        for kb_info in all_kbs:
            kb_id = kb_info.get("kb_id")
            kb_name = kb_info.get("kb_name")
            kb_triggers = kb_info.get("kb_triggers", {})

            if not kb_triggers:
                continue

            triggers = kb_triggers.get("triggers", [])
            for trigger_config in triggers:
                if trigger_config.get("enabled", False):
                    all_triggers.append({
                        "kb_id": kb_id,
                        "kb_name": kb_name,
                        "trigger": trigger_config
                    })

        if not all_triggers:
            logger.debug("No enabled triggers found")
            return

        logger.info(f"Processing {len(all_triggers)} enabled triggers")

        # Process each trigger
        for trigger_info in all_triggers:
            try:
                await self._process_single_trigger(
                    kb_id=trigger_info["kb_id"],
                    kb_name=trigger_info["kb_name"],
                    trigger_config=trigger_info["trigger"]
                )
            except Exception as e:
                logger.error(
                    f"Failed to process trigger: kb_name={trigger_info['kb_name']}, "
                    f"trigger_id={trigger_info['trigger'].get('trigger_id')}, "
                    f"error={str(e)}"
                )

        logger.debug("Trigger detection cycle completed")

    async def _process_single_trigger(
        self,
        kb_id: str,
        kb_name: str,
        trigger_config: dict
    ) -> None:
        """Process a single trigger for a knowledge base.

        Args:
            kb_id: Knowledge base ID
            kb_name: Knowledge base name
            trigger_config: Trigger configuration dict (from ES)
        """
        from core.model.trigger import TriggerConfig

        # Parse trigger configuration
        trigger = TriggerConfig(**trigger_config)
        trigger_id = trigger.trigger_id

        logger.debug(
            f"Processing trigger: trigger_id={trigger_id}, kb_name={kb_name}"
        )

        # KB data is stored in index named after kb_name
        index_name = kb_name

        # Detect matching records
        matching_records = self.detector.detect_matching_records(
            trigger=trigger,
            kb_id=kb_id,
            kb_name=kb_name,
            index_name=index_name,
            size=settings.trigger_config.batch_size
        )

        if not matching_records:
            logger.debug(
                f"No matching records found: trigger_id={trigger_id}, kb_name={kb_name}"
            )
            return

        logger.info(
            f"Found {len(matching_records)} matching records: "
            f"trigger_id={trigger_id}, kb_name={kb_name}"
        )

        # Execute trigger callback
        execution = await self.executor.execute_trigger(
            trigger=trigger,
            records=matching_records,
            kb_id=kb_id,
            kb_name=kb_name
        )

        # Write back updated data from HTTP response
        if trigger.update_data_enabled and execution.status == "success" and execution.updated_records:
            self.detector.bulk_update_records(
                index_name=index_name,
                updated_records=execution.updated_records,
                kb_id=kb_id,
                kb_name=kb_name
            )
            logger.info(
                f"Trigger executed successfully: trigger_id={trigger_id}, "
                f"kb_name={kb_name}, triggered={len(execution.sample_ids)}, "
                f"updated={len(execution.updated_records)}"
            )
        elif execution.status == "success":
            logger.info(
                f"Trigger executed successfully: trigger_id={trigger_id}, "
                f"kb_name={kb_name}, records={len(execution.sample_ids)}, "
                f"update_data_enabled={trigger.update_data_enabled}, "
                f"updated_count={len(execution.updated_records) if execution.updated_records else 0}"
            )

        # Record execution history
        self.history_manager.add_execution(execution)

        # Update trigger_execution_log for deduplication
        if execution.status == "success":
            sample_ids = execution.sample_ids
            self.detector.update_trigger_execution_log(
                index_name=index_name,
                sample_ids=sample_ids,
                trigger_id=trigger_id
            )
        else:
            logger.warning(
                f"Trigger execution failed: trigger_id={trigger_id}, "
                f"kb_name={kb_name}, error={execution.error_message}"
            )

    async def manual_trigger(
        self,
        kb_name: str,
        trigger_id: str,
        sample_ids: List[str],
        dry_run: bool = False
    ) -> TriggerExecutionStatus:
        """Manually execute a trigger for specific sample IDs.

        Args:
            kb_name: Knowledge base name
            trigger_id: Trigger ID to execute
            sample_ids: List of sample IDs to trigger
            dry_run: If True, validate without executing HTTP callback

        Returns:
            TriggerExecutionStatus with execution results
        """
        # Get KB info
        kb_info_list = self.kb_manager.kb_info_search_name(kb_name)
        if not kb_info_list or len(kb_info_list) == 0:
            raise ValueError(f"Knowledge base not found: {kb_name}")

        kb_info = kb_info_list[0]
        kb_id = kb_info.get("kb_id")

        # Get trigger configuration
        kb_triggers = kb_info.get("kb_triggers", {})
        triggers = kb_triggers.get("triggers", [])

        trigger_config = None
        for t in triggers:
            if t.get("trigger_id") == trigger_id:
                trigger_config = t
                break

        if not trigger_config:
            raise ValueError(f"Trigger not found: {trigger_id}")

        # Parse trigger
        from core.model.trigger import TriggerConfig
        trigger = TriggerConfig(**trigger_config)

        # Fetch records by sample IDs (KB data is stored in index named after kb_name)
        index_name = kb_name
        records = self._fetch_records_by_sample_ids(index_name, sample_ids)

        if not records:
            raise ValueError(f"No records found for sample_ids: {sample_ids}")

        # Create execution status
        execution = TriggerExecutionStatus(
            kb_id=kb_id,
            kb_name=kb_name,
            trigger_id=trigger_id,
            trigger_name=trigger.trigger_name,
            sample_ids=sample_ids,
            status="pending"
        )

        if dry_run:
            execution.status = "success"
            execution.response_body = f"Dry run: Would trigger {len(sample_ids)} records"
            return execution

        # Execute trigger
        execution = await self.executor.execute_trigger(
            trigger=trigger,
            records=records,
            kb_id=kb_id,
            kb_name=kb_name
        )

        # Write back updated data from HTTP response
        if trigger.update_data_enabled and execution.status == "success" and execution.updated_records:
            self.detector.bulk_update_records(
                index_name=index_name,
                updated_records=execution.updated_records,
                kb_id=kb_id,
                kb_name=kb_name
            )
            logger.info(
                f"Manual trigger executed successfully: trigger_id={trigger_id}, "
                f"kb_name={kb_name}, triggered={len(sample_ids)}, "
                f"updated={len(execution.updated_records)}"
            )
        elif execution.status == "success":
            logger.info(
                f"Manual trigger executed successfully: trigger_id={trigger_id}, "
                f"kb_name={kb_name}, records={len(sample_ids)}, "
                f"update_data_enabled={trigger.update_data_enabled}, "
                f"updated_count={len(execution.updated_records) if execution.updated_records else 0}"
            )

        # Record history
        self.history_manager.add_execution(execution)

        # Update trigger_execution_log if successful
        if execution.status == "success":
            self.detector.update_trigger_execution_log(
                index_name=index_name,
                sample_ids=sample_ids,
                trigger_id=trigger_id
            )

        return execution

    def _fetch_records_by_sample_ids(
        self,
        index_name: str,
        sample_ids: List[str]
    ) -> List[dict]:
        """Fetch records by their sample IDs.

        Args:
            index_name: Elasticsearch index name
            sample_ids: List of sample IDs to fetch

        Returns:
            List of records (empty list if not found)
        """
        try:
            # Build terms query for multiple sample IDs
            response = settings.es_client.search(
                index=index_name,
                body={
                    "query": {
                        "terms": {
                            "sys_sample_id": sample_ids
                        }
                    },
                    "size": len(sample_ids)
                },
                _source=True
            )

            hits = response.get("hits", {}).get("hits", [])
            records = [hit["_source"] for hit in hits]

            logger.debug(f"Fetched {len(records)} records for {len(sample_ids)} sample IDs")
            return records

        except Exception as e:
            logger.error(f"Failed to fetch records by sample_ids: {str(e)}")
            return []

    def get_stats(self) -> dict:
        """Get trigger manager statistics for monitoring.

        Returns:
            Dictionary with manager and executor stats
        """
        return {
            "is_running": self.is_running,
            "executor_stats": self.executor.get_stats()
        }
