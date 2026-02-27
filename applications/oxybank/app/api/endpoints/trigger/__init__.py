"""Trigger API endpoints for knowledge base automation.

This module provides REST API endpoints for managing triggers and
querying execution history.
"""
from fastapi import APIRouter

from app.api.endpoints.trigger import crud, history, manual

router = APIRouter(prefix="/trigger", tags=["trigger"])

# Include trigger CRUD routes
router.include_router(crud.router)

# Include manual trigger route
router.include_router(manual.router)

# Include history query routes
router.include_router(history.router)

# Alias for compatibility with router.py
trigger = router
