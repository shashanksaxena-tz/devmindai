"""API routes for DevMind."""

from fastapi import APIRouter

from src.api.routes.security import router as security_router
from src.api.routes.reviews import router as reviews_router

api_router = APIRouter()

api_router.include_router(security_router, prefix="/security", tags=["Security"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])

__all__ = ["api_router"]
