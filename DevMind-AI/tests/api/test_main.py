"""Tests for main FastAPI application."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    """Create test client."""
    from src.api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Health endpoint should return OK status."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_ready_check(self, client: AsyncClient):
        """Ready endpoint should return readiness status."""
        response = await client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestAPIInfo:
    """Test suite for API information endpoints."""

    @pytest.mark.asyncio
    async def test_root_redirects_to_docs(self, client: AsyncClient):
        """Root should redirect to API documentation."""
        response = await client.get("/", follow_redirects=False)

        assert response.status_code == 307
        assert response.headers["location"] == "/docs"

    @pytest.mark.asyncio
    async def test_openapi_schema_available(self, client: AsyncClient):
        """OpenAPI schema should be available."""
        response = await client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "DevMind AI"
