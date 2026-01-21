"""API routes for DevMind."""

from fastapi import APIRouter

from src.api.routes.security import router as security_router
from src.api.routes.reviews import router as reviews_router
from src.api.routes.tests import router as tests_router
from src.api.routes.debt import router as debt_router
from src.api.routes.docs import router as docs_router
from src.api.routes.incidents import router as incidents_router
from src.api.routes.migrations import router as migrations_router
from src.api.routes.queries import router as queries_router
from src.api.routes.adrs import router as adrs_router

api_router = APIRouter()

api_router.include_router(security_router, prefix="/security", tags=["Security"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(tests_router, prefix="/tests", tags=["Tests"])
api_router.include_router(debt_router, prefix="/debt", tags=["Debt"])
api_router.include_router(docs_router, prefix="/docs", tags=["Docs"])
api_router.include_router(incidents_router, prefix="/incidents", tags=["Incidents"])
api_router.include_router(migrations_router, prefix="/migrations", tags=["Migrations"])
api_router.include_router(queries_router, prefix="/queries", tags=["Queries"])
api_router.include_router(adrs_router, prefix="/adrs", tags=["ADRs"])

__all__ = ["api_router"]
