"""API routes for DevMind."""

from fastapi import APIRouter

from src.api.routes.security import router as security_router
from src.api.routes.reviews import router as reviews_router
from src.api.routes.tests import router as tests_router
from src.api.routes.debt import router as debt_router

api_router = APIRouter()

api_router.include_router(security_router, prefix="/security", tags=["Security"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(tests_router, prefix="/tests", tags=["Tests"])
api_router.include_router(debt_router, prefix="/debt", tags=["Debt"])

__all__ = ["api_router"]
