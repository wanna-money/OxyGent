"""HTTP executor for trigger callbacks.

This module handles HTTP request execution with retry logic, batch processing,
and proper error handling for trigger callbacks.
"""
import asyncio
import json
from typing import Any, Dict, List

import httpx
from loguru import logger

from core.config import settings
from core.model.trigger import TriggerConfig, TriggerExecutionStatus
from core.trigger.concurrency import ConcurrencyManager


class TriggerExecutor:
    """Executes HTTP callbacks for knowledge base triggers.

    Features:
    - Automatic retry with configurable attempts and intervals
    - Batch mode support (pack multiple records into one request)
    - Concurrent execution with Semaphore + rate limiting
    - Comprehensive error logging and tracking
    """

    def __init__(self, concurrency_manager: ConcurrencyManager | None = None):
        """Initialize trigger executor.

        Args:
            concurrency_manager: Optional custom concurrency manager.
                                If not provided, creates default from settings.
        """
        if concurrency_manager is None:
            concurrency_manager = ConcurrencyManager(
                max_concurrent=settings.trigger_config.max_concurrent_triggers,
                max_qps=settings.trigger_config.max_qps
            )
        self.concurrency_manager = concurrency_manager

    async def execute_trigger(
        self,
        trigger: TriggerConfig,
        records: List[Dict[str, Any]],
        kb_id: str,
        kb_name: str
    ) -> TriggerExecutionStatus:
        """Execute trigger callback for given records.

        Handles both batch and single-record modes with automatic retry.
        Parses HTTP response to extract updated data for ES write-back.

        Args:
            trigger: Trigger configuration
            records: List of matching knowledge base records
            kb_id: Knowledge base ID
            kb_name: Knowledge base name

        Returns:
            TriggerExecutionStatus with execution results and updated data
        """
        execution = TriggerExecutionStatus(
            kb_id=kb_id,
            kb_name=kb_name,
            trigger_id=trigger.trigger_id,
            trigger_name=trigger.trigger_name,
            sample_ids=[r.get("sys_sample_id") or r.get("_id") for r in records],
            status="pending"
        )

        if not records:
            execution.status = "success"
            execution.response_body = "No records to process"
            return execution

        try:
            if trigger.batch_mode:
                await self._execute_batch_trigger(trigger, records, execution)
            else:
                await self._execute_single_trigger(trigger, records, execution)

        except Exception as e:
            logger.error(
                f"Trigger execution failed: trigger_id={trigger.trigger_id}, "
                f"kb_name={kb_name}, error={str(e)}"
            )
            execution.status = "failed"
            execution.error_message = str(e)

        return execution

    async def _execute_batch_trigger(
        self,
        trigger: TriggerConfig,
        records: List[Dict[str, Any]],
        execution: TriggerExecutionStatus
    ) -> None:
        """Execute trigger in batch mode (pack multiple records into requests).

        Args:
            trigger: Trigger configuration
            records: List of matching records
            execution: Execution status to update
        """
        batch_size = trigger.batch_size or 50
        total_records = len(records)

        logger.info(
            f"Executing batch trigger: trigger_id={trigger.trigger_id}, "
            f"total_records={total_records}, batch_size={batch_size}"
        )

        last_error = None
        for attempt in range(trigger.retry_times):
            try:
                # Process in batches
                for i in range(0, total_records, batch_size):
                    batch = records[i:i + batch_size]
                    payload = {"items": batch}

                    # Send request and get updated records
                    updated_records = await self._send_http_request(
                        trigger, payload, execution
                    )

                    # If successful, update status
                    if execution.status == "success":
                        # Collect updated records
                        execution.updated_records.extend(updated_records)
                        execution.updated_count = len(execution.updated_records)

                        logger.info(
                            f"Batch trigger succeeded: trigger_id={trigger.trigger_id}, "
                            f"batch={i // batch_size + 1}/{(total_records + batch_size - 1) // batch_size}, "
                            f"records={len(batch)}, updated={len(updated_records)}"
                        )
                        return  # Success, exit retry loop

            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                last_error = str(e)
                execution.retry_count = attempt + 1
                logger.warning(
                    f"Batch trigger attempt {attempt + 1}/{trigger.retry_times} failed: "
                    f"trigger_id={trigger.trigger_id}, error={e}"
                )

                # Don't wait on last attempt
                if attempt < trigger.retry_times - 1:
                    await asyncio.sleep(trigger.retry_interval)

        # All retries failed
        execution.status = "failed"
        execution.error_message = last_error or "Max retries exceeded"

    async def _execute_single_trigger(
        self,
        trigger: TriggerConfig,
        records: List[Dict[str, Any]],
        execution: TriggerExecutionStatus
    ) -> None:
        """Execute trigger in single-record mode (one HTTP call per record).

        Args:
            trigger: Trigger configuration
            records: List of matching records
            execution: Execution status to update
        """
        total_records = len(records)

        logger.info(
            f"Executing single-record trigger: trigger_id={trigger.trigger_id}, "
            f"total_records={total_records}"
        )

        successful_count = 0
        failed_count = 0
        errors = []

        for idx, record in enumerate(records, 1):
            last_error = None
            for attempt in range(trigger.retry_times):
                try:
                    # Send request and get updated record
                    updated_records = await self._send_http_request(
                        trigger, record, execution
                    )

                    if execution.status == "success":
                        successful_count += 1
                        # Collect updated record
                        if updated_records:
                            execution.updated_records.extend(updated_records)
                            execution.updated_count = len(execution.updated_records)
                        break  # Success, move to next record
                        break  # Success, move to next record

                except (httpx.HTTPError, asyncio.TimeoutError) as e:
                    last_error = str(e)
                    logger.warning(
                        f"Single-record trigger attempt {attempt + 1}/{trigger.retry_times} failed: "
                        f"trigger_id={trigger.trigger_id}, record={idx}/{total_records}, error={e}"
                    )

                    if attempt < trigger.retry_times - 1:
                        await asyncio.sleep(trigger.retry_interval)

            else:
                # All retries failed for this record
                failed_count += 1
                errors.append(f"Record {idx}: {last_error}")

        # Update execution status based on results
        execution.retry_count = total_records  # Total records processed
        if failed_count == 0:
            execution.status = "success"
            execution.response_body = f"All {successful_count} records processed successfully"
        elif successful_count > 0:
            execution.status = "failed"
            execution.error_message = (
                f"Partial failure: {successful_count} succeeded, {failed_count} failed. "
                f"Errors: {'; '.join(errors[:5])}"
            )
        else:
            execution.status = "failed"
            execution.error_message = f"All {failed_count} records failed. Errors: {'; '.join(errors[:5])}"

    async def _send_http_request(
        self,
        trigger: TriggerConfig,
        payload: Dict[str, Any],
        execution: TriggerExecutionStatus
    ) -> List[Dict[str, Any]]:
        """Send HTTP request with concurrency control and parse response.

        Args:
            trigger: Trigger configuration
            payload: Request payload
            execution: Execution status to update

        Returns:
            List of updated records from HTTP response

        Raises:
            httpx.HTTPError: On HTTP errors
            asyncio.TimeoutError: On timeout
        """
        url = trigger.url
        headers = trigger.http_headers
        method = trigger.http_method.lower()
        timeout = trigger.timeout

        # Use concurrency manager to control rate and concurrency
        async def make_request():
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await getattr(client, method)(
                    url,
                    json=payload,
                    headers=headers
                )

                # Update execution with response details
                execution.http_status_code = response.status_code

                if response.status_code >= 400:
                    error_text = response.text[:500]  # Truncate large responses
                    raise httpx.HTTPStatusError(
                        f"HTTP {response.status_code}: {error_text}",
                        request=response.request,
                        response=response
                    )

                # Store response body (truncated if large)
                response_text = response.text
                execution.response_body = (
                    response_text[:1000] + "..." if len(response_text) > 1000
                    else response_text
                )
                execution.status = "success"

                logger.debug(
                    f"HTTP request succeeded: method={method.upper()}, url={url}, "
                    f"status={response.status_code}"
                )

                return response

        # Execute with concurrency control
        response = await self.concurrency_manager.execute(make_request())

        # Parse response to extract updated records
        return self._parse_response(trigger, response)

    def _parse_response(
        self,
        trigger: TriggerConfig,
        response: httpx.Response
    ) -> List[Dict[str, Any]]:
        """Parse HTTP response to extract updated records.

        Supports two response formats:
        1. Single record: {"field1": "value1", "field2": "value2", ...}
        2. Batch records: {"items": [{"field1": "value1", ...}, ...]}

        Args:
            trigger: Trigger configuration
            response: HTTP response object

        Returns:
            List of updated records (empty if parsing fails or update disabled)
        """
        if not trigger.update_data_enabled:
            logger.debug(f"Data update disabled for trigger: {trigger.trigger_id}")
            return []

        try:
            response_json = response.json()

            # Batch mode response: {"items": [...]}
            if trigger.batch_mode:
                if isinstance(response_json, dict) and "items" in response_json:
                    items = response_json["items"]
                    if isinstance(items, list):
                        logger.info(
                            f"Parsed batch response: {len(items)} updated records"
                        )
                        return items
                    else:
                        logger.warning(
                            f"Batch response 'items' is not a list: {type(items)}"
                        )
                        return []

            # Single record response: {field1: value1, ...}
            elif isinstance(response_json, dict):
                # Check if it's a batch response incorrectly formatted
                if "items" in response_json:
                    logger.warning(
                        f"Non-batch trigger received batch response format"
                    )
                logger.info("Parsed single record response")
                return [response_json]

            # Unexpected format
            else:
                logger.warning(
                    f"Unexpected response format: {type(response_json)}, "
                    f"expected dict or list"
                )
                return []

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics for monitoring.

        Returns:
            Dictionary with concurrency and rate limiter stats
        """
        return self.concurrency_manager.get_stats()
