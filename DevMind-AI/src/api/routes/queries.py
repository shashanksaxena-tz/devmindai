"""API routes for Query Optimizer."""

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.agents.query_optimizer.agent import QueryOptimizerAgent
from src.agents.base import AgentContext
from src.core.llm import get_llm_router
from src.core.auth import get_current_user

router = APIRouter()

@router.post("/analyze")
async def analyze_query(
    payload: Dict[str, Any],
    current_user: Any = Depends(get_current_user),
) -> Dict[str, Any]:
    """Analyze and optimize a SQL query.

    Payload should contain:
    - sql: The SQL query string
    - explain: (Optional) The EXPLAIN output (JSON or text)
    - repository_id: (Optional) Repository ID
    """
    sql = payload.get("sql")
    if not sql:
        raise HTTPException(status_code=400, detail="SQL query is required")

    explain = payload.get("explain")
    repository_id = payload.get("repository_id")

    # Initialize agent
    router = get_llm_router()
    agent = QueryOptimizerAgent(router)

    # Create context
    context = AgentContext(
        repository_id=repository_id,
        user_id=str(current_user.id) if hasattr(current_user, "id") else None,
        metadata={"task": "optimize_query"}
    )

    # Execute agent
    result = await agent.run(context, sql=sql, explain=explain)

    if "error" in result and result.get("success") is False:
        raise HTTPException(status_code=500, detail=result["error"])

    return result
