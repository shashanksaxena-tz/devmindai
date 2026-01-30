"""API client for communicating with DevMind AI backend."""

import os
from typing import Any

import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000")


class DevMindAPIClient:
    """Client for DevMind AI REST API."""

    def __init__(self, base_url: str | None = None, token: str | None = None):
        """Initialize the API client.

        Args:
            base_url: Base URL for the API (defaults to API_URL env var)
            token: Optional authentication token
        """
        self.base_url = base_url or API_URL
        self.token = token
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=30.0,
            headers=self._get_headers(),
        )

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Make an API request.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments

        Returns:
            Response JSON or None on error
        """
        try:
            response = self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": str(e), "status_code": e.response.status_code}
        except httpx.RequestError as e:
            return {"error": str(e), "status_code": None}

    # Health
    def health_check(self) -> dict[str, Any] | None:
        """Check API health."""
        return self._request("GET", "/health")

    # Repositories
    def list_repositories(self) -> dict[str, Any] | None:
        """List all connected repositories."""
        return self._request("GET", "/api/v1/repos")

    def get_repository(self, repo_id: str) -> dict[str, Any] | None:
        """Get repository details."""
        return self._request("GET", f"/api/v1/repos/{repo_id}")

    # Security
    def trigger_security_scan(self, repo_id: str) -> dict[str, Any] | None:
        """Trigger a security scan."""
        return self._request("POST", f"/api/v1/security/{repo_id}/scan")

    def list_vulnerabilities(self, repo_id: str) -> dict[str, Any] | None:
        """List vulnerabilities for a repository."""
        return self._request("GET", f"/api/v1/security/{repo_id}/vulns")

    def get_security_summary(self, repo_id: str) -> dict[str, Any] | None:
        """Get security summary for a repository."""
        return self._request("GET", f"/api/v1/security/{repo_id}/summary")

    # Code Reviews
    def trigger_review(
        self,
        repo_id: str,
        pr_number: int | None = None,
        diff: str | None = None,
    ) -> dict[str, Any] | None:
        """Trigger a code review."""
        data = {}
        if pr_number:
            data["pr_number"] = pr_number
        if diff:
            data["diff"] = diff
        return self._request("POST", f"/api/v1/reviews/repos/{repo_id}/review", json=data)

    def list_reviews(self, repo_id: str) -> dict[str, Any] | None:
        """List reviews for a repository."""
        return self._request("GET", f"/api/v1/reviews/repos/{repo_id}/reviews")

    def get_review(self, review_id: str) -> dict[str, Any] | None:
        """Get review details."""
        return self._request("GET", f"/api/v1/reviews/reviews/{review_id}")

    def get_job_status(self, job_id: str) -> dict[str, Any] | None:
        """Get job status."""
        return self._request("GET", f"/api/v1/reviews/jobs/{job_id}/status")

    # Tests
    def generate_tests(
        self,
        repo_id: str,
        files: dict[str, str],
        framework: str = "pytest",
    ) -> dict[str, Any] | None:
        """Generate tests for code."""
        return self._request(
            "POST",
            f"/api/v1/tests/{repo_id}/generate",
            json={"files": files, "framework": framework},
        )

    # Technical Debt
    def analyze_debt(self, repo_id: str) -> dict[str, Any] | None:
        """Analyze technical debt."""
        return self._request("POST", f"/api/v1/debt/{repo_id}/analyze")

    def get_debt_report(self, repo_id: str) -> dict[str, Any] | None:
        """Get debt analysis report."""
        return self._request("GET", f"/api/v1/debt/{repo_id}/report")

    # Incidents
    def list_incidents(self, org_id: str | None = None) -> dict[str, Any] | None:
        """List incidents."""
        params = {"org_id": org_id} if org_id else {}
        return self._request("GET", "/api/v1/incidents", params=params)

    def get_incident(self, incident_id: str) -> dict[str, Any] | None:
        """Get incident details."""
        return self._request("GET", f"/api/v1/incidents/{incident_id}")

    # Documentation
    def generate_docs(
        self,
        repo_id: str,
        files: dict[str, str],
        format: str = "markdown",
    ) -> dict[str, Any] | None:
        """Generate documentation."""
        return self._request(
            "POST",
            f"/api/v1/docs/{repo_id}/generate",
            json={"files": files, "format": format},
        )

    # Pipelines
    def generate_pipeline(
        self,
        repo_id: str,
        files: dict[str, str],
        platform: str = "github_actions",
    ) -> dict[str, Any] | None:
        """Generate CI/CD pipeline."""
        return self._request(
            "POST",
            f"/api/v1/pipelines/{repo_id}/generate",
            json={"files": files, "platform": platform},
        )

    # ADRs
    def capture_adr(
        self,
        messages: list[dict[str, str]],
        source: str = "manual",
    ) -> dict[str, Any] | None:
        """Capture architecture decision."""
        return self._request(
            "POST",
            "/api/v1/adrs/capture",
            json={"messages": messages, "source": source},
        )

    def search_adrs(self, query: str) -> dict[str, Any] | None:
        """Search ADRs."""
        return self._request("POST", "/api/v1/adrs/search", json={"query": query})

    def close(self):
        """Close the client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# Convenience function for quick access
def get_client(token: str | None = None) -> DevMindAPIClient:
    """Get an API client instance."""
    return DevMindAPIClient(token=token)
