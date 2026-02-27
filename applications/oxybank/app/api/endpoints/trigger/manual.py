"""Manual trigger API endpoint.

Provides endpoint for manually executing triggers for specific sample IDs.
"""
from fastapi import APIRouter, HTTPException, status

from app.api.models import APIResponse
from core.model.trigger import ManualTriggerRequest, TriggerExecutionStatus
from core.services.trigger_service import TriggerService

router = APIRouter()

# Initialize service
trigger_service = TriggerService()


@router.post("/{kb_name}/{trigger_id}/manual", response_model=APIResponse)
async def manual_trigger(
    kb_name: str,
    trigger_id: str,
    request: ManualTriggerRequest
) -> APIResponse:
    """Manually execute a trigger for specific sample IDs.

    Args:
        kb_name: Knowledge base name
        trigger_id: Trigger ID to execute
        request: Manual trigger request with sample_ids and dry_run flag

    Returns:
        APIResponse with execution status

    Raises:
        HTTPException: If validation fails
    """
    try:
        execution = await trigger_service.manual_trigger(
            kb_name=kb_name,
            trigger_id=trigger_id,
            request=request
        )
        return APIResponse(
            code=200,
            msg="Manual trigger executed successfully",
            data=execution.model_dump()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute manual trigger: {str(e)}"
        )
