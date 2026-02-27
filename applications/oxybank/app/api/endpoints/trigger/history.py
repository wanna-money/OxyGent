"""History query API endpoints.

Provides endpoints for querying trigger execution history.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.api.models import APIResponse
from core.services.trigger_service import TriggerService

router = APIRouter()

# Initialize service
trigger_service = TriggerService()


@router.get("/history/{kb_name}", response_model=APIResponse)
async def query_history_by_kb(
    kb_name: str,
    trigger_id: Optional[str] = Query(None, description="Filter by trigger ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by execution status"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD HH:MM:SS)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Records per page")
) -> APIResponse:
    """Query trigger execution history for a knowledge base.

    Args:
        kb_name: Knowledge base name
        trigger_id: Optional filter by trigger ID
        status: Optional filter by execution status (pending/success/failed)
        start_date: Optional start date filter
        end_date: Optional end date filter
        page: Page number (1-based)
        page_size: Records per page (max 100)

    Returns:
        APIResponse with execution history
    """
    try:
        # Parse date strings
        start_dt = None
        end_dt = None

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use 'YYYY-MM-DD HH:MM:SS'"
                )

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use 'YYYY-MM-DD HH:MM:SS'"
                )

        result = trigger_service.query_history(
            kb_name=kb_name,
            trigger_id=trigger_id,
            status=status_filter,
            start_date=start_dt,
            end_date=end_dt,
            page=page,
            page_size=page_size
        )

        return APIResponse(
            code=200,
            msg="History retrieved successfully",
            data=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query history: {str(e)}"
        )


@router.get("/history/{kb_name}/{trigger_id}", response_model=APIResponse)
async def query_history_by_trigger(
    kb_name: str,
    trigger_id: str,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by execution status"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD HH:MM:SS)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Records per page")
) -> APIResponse:
    """Query execution history for a specific trigger.

    Args:
        kb_name: Knowledge base name
        trigger_id: Trigger ID
        status: Optional filter by execution status
        start_date: Optional start date filter
        end_date: Optional end date filter
        page: Page number (1-based)
        page_size: Records per page (max 100)

    Returns:
        APIResponse with execution history
    """
    try:
        # Parse date strings
        start_dt = None
        end_dt = None

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use 'YYYY-MM-DD HH:MM:SS'"
                )

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use 'YYYY-MM-DD HH:MM:SS'"
                )

        result = trigger_service.query_history(
            kb_name=kb_name,
            trigger_id=trigger_id,
            status=status_filter,
            start_date=start_dt,
            end_date=end_dt,
            page=page,
            page_size=page_size
        )

        return APIResponse(
            code=200,
            msg="History retrieved successfully",
            data=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query history: {str(e)}"
        )


@router.get("/stats/{kb_name}", response_model=APIResponse)
async def get_trigger_stats(
    kb_name: str,
    trigger_id: Optional[str] = Query(None, description="Filter by trigger ID")
) -> APIResponse:
    """Get execution statistics for a knowledge base.

    Args:
        kb_name: Knowledge base name
        trigger_id: Optional filter by trigger ID

    Returns:
        APIResponse with execution statistics
    """
    try:
        stats = trigger_service.get_stats(
            kb_name=kb_name,
            trigger_id=trigger_id
        )

        return APIResponse(
            code=200,
            msg="Statistics retrieved successfully",
            data=stats
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )
