"""Service layer for trigger system business logic.

This module provides high-level business operations for trigger management,
including CRUD operations, manual triggering, and history queries.
"""
from datetime import datetime
from typing import List, Optional

from loguru import logger

from core.config import settings
from core.storer.doc_manager.es_kb_base_manager import ElasticsearchKbBaseManager
from core.model.trigger import (
    TriggerConfig,
    TriggerConfigWrapper,
    TriggerCreateRequest,
    TriggerUpdateRequest,
    TriggerResponse,
    ManualTriggerRequest,
    TriggerExecutionStatus
)
from core.storer.doc_manager.es_kb_base_manager import ElasticsearchKbBaseManager
from core.storer.doc_manager.trigger_history_manager import ElasticsearchTriggerHistoryManager
from core.trigger.manager import TriggerManager


class TriggerService:
    """Business logic layer for trigger operations.

    Provides CRUD operations for triggers, manual trigger execution,
    and history querying with proper validation and error handling.
    """

    def __init__(
        self,
        kb_manager: Optional[ElasticsearchKbBaseManager] = None,
        history_manager: Optional[ElasticsearchTriggerHistoryManager] = None,
        trigger_manager: Optional[TriggerManager] = None
    ):
        """Initialize trigger service.

        Args:
            kb_manager: Knowledge base manager (optional)
            history_manager: Trigger history manager (optional)
            trigger_manager: Trigger manager for execution (optional)
        """
        self.kb_manager = kb_manager or ElasticsearchKbBaseManager(settings.es_client)
        self.history_manager = history_manager or ElasticsearchTriggerHistoryManager(settings.es_client)
        self.trigger_manager = trigger_manager or TriggerManager()

    def create_trigger(
        self,
        kb_name: str,
        request: TriggerCreateRequest
    ) -> TriggerResponse:
        """Create a new trigger for a knowledge base.

        Args:
            kb_name: Knowledge base name
            request: Trigger creation request

        Returns:
            Created trigger response

        Raises:
            ValueError: If KB not found or validation fails
        """
        # Check if KB exists
        kb_info_list = self.kb_manager.kb_info_search_name(kb_name)
        if not kb_info_list or len(kb_info_list) == 0:
            raise ValueError(f"Knowledge base not found: {kb_name}")

        kb_info = kb_info_list[0]
        kb_id = kb_info.get("kb_id")

        # Get existing triggers
        kb_triggers_data = kb_info.get("kb_triggers", {})
        if kb_triggers_data:
            wrapper = TriggerConfigWrapper(**kb_triggers_data)
            existing_triggers = wrapper.triggers
        else:
            existing_triggers = []

        # Create new trigger (auto-generates trigger_id)
        new_trigger = TriggerConfig(**request.model_dump())

        # Check for duplicate trigger name
        for t in existing_triggers:
            if t.trigger_name == new_trigger.trigger_name:
                raise ValueError(f"Trigger name already exists: {new_trigger.trigger_name}")

        # Add to list
        existing_triggers.append(new_trigger)
        wrapper = TriggerConfigWrapper(triggers=existing_triggers)

        # Update KB info
        self.kb_manager.kb_update(
            kb_name=kb_name,
            update_fields={
                "kb_triggers": wrapper.model_dump(),
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

        logger.info(
            f"Created trigger: trigger_id={new_trigger.trigger_id}, "
            f"trigger_name={new_trigger.trigger_name}, kb_name={kb_name}"
        )

        return self._to_trigger_response(new_trigger)

    def get_triggers(self, kb_name: str) -> List[TriggerResponse]:
        """Get all triggers for a knowledge base.

        Args:
            kb_name: Knowledge base name

        Returns:
            List of trigger responses (empty list if none)

        Raises:
            ValueError: If KB not found
        """
        # Check if KB exists
        kb_info_list = self.kb_manager.kb_info_search_name(kb_name)
        if not kb_info_list or len(kb_info_list) == 0:
            raise ValueError(f"Knowledge base not found: {kb_name}")

        kb_info = kb_info_list[0]

        # Get triggers
        kb_triggers_data = kb_info.get("kb_triggers", {})
        if not kb_triggers_data:
            return []

        wrapper = TriggerConfigWrapper(**kb_triggers_data)
        return [
            self._to_trigger_response(trigger)
            for trigger in wrapper.triggers
        ]

    def get_trigger(
        self,
        kb_name: str,
        trigger_id: str
    ) -> Optional[TriggerResponse]:
        """Get a specific trigger by ID.

        Args:
            kb_name: Knowledge base name
            trigger_id: Trigger ID

        Returns:
            Trigger response or None if not found

        Raises:
            ValueError: If KB not found
        """
        triggers = self.get_triggers(kb_name)
        for trigger in triggers:
            if trigger.trigger_id == trigger_id:
                return trigger
        return None

    def update_trigger(
        self,
        kb_name: str,
        trigger_id: str,
        request: TriggerUpdateRequest
    ) -> TriggerResponse:
        """Update an existing trigger.

        Args:
            kb_name: Knowledge base name
            trigger_id: Trigger ID
            request: Update request (partial fields)

        Returns:
            Updated trigger response

        Raises:
            ValueError: If KB or trigger not found
        """
        # Get KB info
        kb_info_list = self.kb_manager.kb_info_search_name(kb_name)
        if not kb_info_list or len(kb_info_list) == 0:
            raise ValueError(f"Knowledge base not found: {kb_name}")

        kb_info = kb_info_list[0]

        # Get existing triggers
        kb_triggers_data = kb_info.get("kb_triggers", {})
        if not kb_triggers_data:
            raise ValueError(f"No triggers found for KB: {kb_name}")

        wrapper = TriggerConfigWrapper(**kb_triggers_data)
        triggers = wrapper.triggers

        # Find trigger to update
        trigger_to_update = None
        for idx, trigger in enumerate(triggers):
            if trigger.trigger_id == trigger_id:
                trigger_to_update = trigger
                break

        if not trigger_to_update:
            raise ValueError(f"Trigger not found: {trigger_id}")

        # Build update dict with only provided fields
        update_dict = request.model_dump(exclude_unset=True)

        # Update trigger fields
        for field, value in update_dict.items():
            if field == "conditions" and value is not None:
                # Replace entire conditions list
                trigger_to_update.conditions = value
            else:
                setattr(trigger_to_update, field, value)

        # Save updated triggers
        self.kb_manager.kb_update(
            kb_name=kb_name,
            update_fields={
                "kb_triggers": wrapper.model_dump(),
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

        logger.info(f"Updated trigger: trigger_id={trigger_id}, kb_name={kb_name}")

        return self._to_trigger_response(trigger_to_update)

    def delete_trigger(
        self,
        kb_name: str,
        trigger_id: str
    ) -> bool:
        """Delete a trigger from a knowledge base.

        Args:
            kb_name: Knowledge base name
            trigger_id: Trigger ID

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If KB not found
        """
        # Get KB info
        kb_info_list = self.kb_manager.kb_info_search_name(kb_name)
        if not kb_info_list or len(kb_info_list) == 0:
            raise ValueError(f"Knowledge base not found: {kb_name}")

        kb_info = kb_info_list[0]

        # Get existing triggers
        kb_triggers_data = kb_info.get("kb_triggers", {})
        if not kb_triggers_data:
            return False

        wrapper = TriggerConfigWrapper(**kb_triggers_data)
        triggers = wrapper.triggers

        # Find and remove trigger
        original_count = len(triggers)
        triggers = [t for t in triggers if t.trigger_id != trigger_id]

        if len(triggers) == original_count:
            return False  # Trigger not found

        # Save updated triggers
        wrapper.triggers = triggers
        self.kb_manager.kb_update(
            kb_name=kb_name,
            update_fields={
                "kb_triggers": wrapper.model_dump(),
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

        logger.info(f"Deleted trigger: trigger_id={trigger_id}, kb_name={kb_name}")

        return True

    def enable_trigger(
        self,
        kb_name: str,
        trigger_id: str
    ) -> TriggerResponse:
        """Enable a trigger.

        Args:
            kb_name: Knowledge base name
            trigger_id: Trigger ID

        Returns:
            Updated trigger response

        Raises:
            ValueError: If KB or trigger not found
        """
        return self.update_trigger(
            kb_name=kb_name,
            trigger_id=trigger_id,
            request=TriggerUpdateRequest(enabled=True)
        )

    def disable_trigger(
        self,
        kb_name: str,
        trigger_id: str
    ) -> TriggerResponse:
        """Disable a trigger.

        Args:
            kb_name: Knowledge base name
            trigger_id: Trigger ID

        Returns:
            Updated trigger response

        Raises:
            ValueError: If KB or trigger not found
        """
        return self.update_trigger(
            kb_name=kb_name,
            trigger_id=trigger_id,
            request=TriggerUpdateRequest(enabled=False)
        )

    async def manual_trigger(
        self,
        kb_name: str,
        trigger_id: str,
        request: ManualTriggerRequest
    ) -> TriggerExecutionStatus:
        """Manually execute a trigger for specific sample IDs.

        Args:
            kb_name: Knowledge base name
            trigger_id: Trigger ID
            request: Manual trigger request

        Returns:
            Execution status

        Raises:
            ValueError: If KB or trigger not found
        """
        return await self.trigger_manager.manual_trigger(
            kb_name=kb_name,
            trigger_id=trigger_id,
            sample_ids=request.sample_ids,
            dry_run=request.dry_run
        )

    def query_history(
        self,
        kb_name: Optional[str] = None,
        trigger_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """Query trigger execution history.

        Args:
            kb_name: Filter by knowledge base name
            trigger_id: Filter by trigger ID
            status: Filter by execution status
            start_date: Filter by start date
            end_date: Filter by end date
            page: Page number (1-based)
            page_size: Records per page

        Returns:
            Dictionary with 'total', 'page', 'page_size', 'records' keys
        """
        return self.history_manager.query_executions(
            kb_name=kb_name,
            trigger_id=trigger_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )

    def get_stats(
        self,
        kb_name: Optional[str] = None,
        trigger_id: Optional[str] = None
    ) -> dict:
        """Get execution statistics.

        Args:
            kb_name: Filter by knowledge base name (optional)
            trigger_id: Filter by trigger ID (optional)

        Returns:
            Dictionary with execution statistics
        """
        return self.history_manager.get_execution_stats(
            kb_name=kb_name,
            trigger_id=trigger_id
        )

    @staticmethod
    def _to_trigger_response(trigger: TriggerConfig) -> TriggerResponse:
        """Convert TriggerConfig to TriggerResponse.

        Args:
            trigger: Trigger configuration

        Returns:
            Trigger response
        """
        return TriggerResponse(
            trigger_id=trigger.trigger_id,
            trigger_name=trigger.trigger_name,
            url=trigger.url,
            conditions=trigger.conditions,
            http_method=trigger.http_method,
            http_headers=trigger.http_headers,
            batch_mode=trigger.batch_mode,
            batch_size=trigger.batch_size,
            timeout=trigger.timeout,
            retry_times=trigger.retry_times,
            retry_interval=trigger.retry_interval,
            enabled=trigger.enabled,
            update_data_enabled=trigger.update_data_enabled
        )
