"""API routes for CodeMigrator agent."""

from typing import Any, Dict

from fastapi import APIRouter, Depends

from src.agents.code_migrator.agent import CodeMigratorAgent
from src.agents.base import AgentContext, AgentResult
from src.core.auth import get_current_user
from src.core.llm import LLMRouter, get_llm_router

router = APIRouter()


@router.post("/migrate", response_model=AgentResult)
async def migrate_code(
    payload: Dict[str, Any],
    current_user: Any = Depends(get_current_user),
    llm_router: LLMRouter = Depends(get_llm_router),
) -> AgentResult:
    """Run code migration."""
    try:
        agent = CodeMigratorAgent(router=llm_router)

        # Construct context
        context = AgentContext(
            user_id=str(current_user.id) if hasattr(current_user, "id") else "user",
            repository_id=payload.get("repository_id"),
        )

        # Execute agent
        result = await agent.run(context, **payload)

        if isinstance(result, dict) and not result.get("success", True) and "error" in result:
             return AgentResult.fail(result["error"])

        return AgentResult.ok(data=result)

    except Exception as e:
        return AgentResult.fail(str(e))
