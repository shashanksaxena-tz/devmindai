from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from src.agents.debt_analyzer.agent import DebtAnalyzerAgent
from src.agents.base import AgentContext
from src.core.auth import get_current_user

router = APIRouter()

class DebtRequest(BaseModel):
    files: Dict[str, str] = Field(..., description="Map of file paths to content")
    repository_id: Optional[str] = None

class DebtResponse(BaseModel):
    score: int
    grade: str
    total_debt_hours: float
    estimated_cost: float
    metrics: Dict[str, Any]
    debt_items: List[Dict[str, Any]]

@router.post("/analyze", response_model=DebtResponse)
async def analyze_debt(
    request: DebtRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze technical debt for the provided files.
    """
    agent = DebtAnalyzerAgent()
    context = AgentContext(
        user_id=current_user.get("id"),
        repository_id=request.repository_id
    )

    result = await agent.execute(context, files=request.files)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Analysis failed"))

    return result["data"]
