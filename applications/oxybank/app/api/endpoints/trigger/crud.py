"""CRUD API endpoints for trigger management.

Provides endpoints for creating, reading, updating, and deleting triggers.
"""
from typing import List

from fastapi import APIRouter, HTTPException, status

from app.api.models import APIResponse
from core.model.trigger import (
    TriggerCreateRequest,
    TriggerUpdateRequest
)
from core.services.trigger_service import TriggerService

router = APIRouter()

# Initialize service
trigger_service = TriggerService()


@router.post("/{kb_name}/", response_model=APIResponse)
async def create_trigger(
    kb_name: str,
    request: TriggerCreateRequest
) -> APIResponse:
    """Create a new trigger for a knowledge base.

    Args:
        kb_name: Knowledge base name
        request: Trigger creation request

    Returns:
        APIResponse with created trigger

    Raises:
        HTTPException: If validation fails
    """
    try:
        trigger = trigger_service.create_trigger(kb_name, request)
        return APIResponse(
            code=200,
            msg="Trigger created successfully",
            data=trigger.model_dump()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trigger: {str(e)}"
        )


@router.get("/{kb_name}/", response_model=APIResponse)
async def get_triggers(kb_name: str) -> APIResponse:
    """Get all triggers for a knowledge base.

    Args:
        kb_name: Knowledge base name

    Returns:
        APIResponse with list of triggers
    """
    try:
        triggers = trigger_service.get_triggers(kb_name)
        return APIResponse(
            code=200,
            msg="Triggers retrieved successfully",
            data=[t.model_dump() for t in triggers]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve triggers: {str(e)}"
        )


@router.get("/{kb_name}/{trigger_id}", response_model=APIResponse)
async def get_trigger(
    kb_name: str,
    trigger_id: str
) -> APIResponse:
    """Get a specific trigger by ID.

    Args:
        kb_name: Knowledge base name
        trigger_id: Trigger ID

    Returns:
        APIResponse with trigger details

    Raises:
        HTTPException: If trigger not found
    """
    try:
        trigger = trigger_service.get_trigger(kb_name, trigger_id)
        if not trigger:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trigger not found: {trigger_id}"
            )
        return APIResponse(
            code=200,
            msg="Trigger retrieved successfully",
            data=trigger.model_dump()
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trigger: {str(e)}"
        )


@router.put("/{kb_name}/{trigger_id}", response_model=APIResponse)
async def update_trigger(
    kb_name: str,
    trigger_id: str,
    request: TriggerUpdateRequest
) -> APIResponse:
    """Update an existing trigger.

    Args:
        kb_name: Knowledge base name
        trigger_id: Trigger ID
        request: Update request (partial fields)

    Returns:
        APIResponse with updated trigger

    Raises:
        HTTPException: If validation fails
    """
    try:
        trigger = trigger_service.update_trigger(kb_name, trigger_id, request)
        return APIResponse(
            code=200,
            msg="Trigger updated successfully",
            data=trigger.model_dump()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update trigger: {str(e)}"
        )


@router.delete("/{kb_name}/{trigger_id}", response_model=APIResponse)
async def delete_trigger(
    kb_name: str,
    trigger_id: str
) -> APIResponse:
    """Delete a trigger from a knowledge base.

    Args:
        kb_name: Knowledge base name
        trigger_id: Trigger ID

    Returns:
        APIResponse confirming deletion

    Raises:
        HTTPException: If KB not found
    """
    try:
        success = trigger_service.delete_trigger(kb_name, trigger_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trigger not found: {trigger_id}"
            )
        return APIResponse(
            code=200,
            msg="Trigger deleted successfully",
            data={"trigger_id": trigger_id}
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete trigger: {str(e)}"
        )


@router.patch("/{kb_name}/{trigger_id}/enable", response_model=APIResponse)
async def enable_trigger(
    kb_name: str,
    trigger_id: str
) -> APIResponse:
    """Enable a trigger.

    Args:
        kb_name: Knowledge base name
        trigger_id: Trigger ID

    Returns:
        APIResponse with updated trigger

    Raises:
        HTTPException: If validation fails
    """
    try:
        trigger = trigger_service.enable_trigger(kb_name, trigger_id)
        return APIResponse(
            code=200,
            msg="Trigger enabled successfully",
            data=trigger.model_dump()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable trigger: {str(e)}"
        )


@router.patch("/{kb_name}/{trigger_id}/disable", response_model=APIResponse)
async def disable_trigger(
    kb_name: str,
    trigger_id: str
) -> APIResponse:
    """Disable a trigger.

    Args:
        kb_name: Knowledge base name
        trigger_id: Trigger ID

    Returns:
        APIResponse with updated trigger

    Raises:
        HTTPException: If validation fails
    """
    try:
        trigger = trigger_service.disable_trigger(kb_name, trigger_id)
        return APIResponse(
            code=200,
            msg="Trigger disabled successfully",
            data=trigger.model_dump()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable trigger: {str(e)}"
        )
