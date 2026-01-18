"""API routes for DevMind."""

from fastapi import APIRouter

from src.api.routes.security import router as security_router

api_router = APIRouter()

api_router.include_router(security_router, prefix="/security", tags=["Security"])

__all__ = ["api_router"]
