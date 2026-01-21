import pytest
from unittest.mock import MagicMock, AsyncMock
from src.agents.debt_analyzer.agent import DebtAnalyzerAgent
from src.agents.base import AgentContext

@pytest.fixture
def debt_agent():
    return DebtAnalyzerAgent()

@pytest.mark.asyncio
async def test_analyze_python_files(debt_agent):
    # Ensure we have enough tokens to trigger duplication (min_tokens=50)
    # A line like "print('hello world this is a long line to ensure we have enough tokens')"
    long_line = "print('hello world this is a long line to ensure we have enough tokens for duplication detection')\n"

    files = {
        "complex.py": """
def complex_function(x):
    # Still not complex enough for default threshold (15) but let's just test general flow
    if x > 0:
        if x > 1:
            if x > 2:
                if x > 3:
                    if x > 4:
                        if x > 5:
                            return True
    return False
""",
        "duplicate.py": long_line * 10
    }

    context = AgentContext(user_id="test-user")
    result = await debt_agent.execute(context, files=files)

    assert result["success"] is True
    data = result["data"]
    assert "score" in data
    assert "grade" in data

    # We expect duplication items now because we exceeded min_tokens
    dup_items = [i for i in data["debt_items"] if i["category"] == "duplication"]
    assert len(dup_items) > 0

@pytest.mark.asyncio
async def test_high_complexity_trigger(debt_agent):
    code = "def really_complex():\n"
    for i in range(20):
        code += f"    if True: pass\n"

    files = {"super_complex.py": code}
    context = AgentContext(user_id="test-user")
    result = await debt_agent.execute(context, files=files)

    data = result["data"]
    complexity_items = [i for i in data["debt_items"] if i["category"] == "complexity"]
    assert len(complexity_items) == 1
    assert complexity_items[0]["file_path"] == "super_complex.py"

@pytest.mark.asyncio
async def test_duplication_trigger(debt_agent):
    # min_lines=5 in DuplicationDetector, min_tokens=50
    # "line1" is very short.
    line = "this is a significantly longer line of code that should help us reach the fifty token minimum threshold required by the duplication detector\n"
    content = line * 6
    files = {
        "file1.txt": content,
        "file2.txt": content
    }

    context = AgentContext(user_id="test-user")
    result = await debt_agent.execute(context, files=files)

    data = result["data"]
    dup_items = [i for i in data["debt_items"] if i["category"] == "duplication"]
    assert len(dup_items) > 0

@pytest.mark.asyncio
async def test_empty_files(debt_agent):
    context = AgentContext(user_id="test-user")
    result = await debt_agent.execute(context, files={})

    assert result["success"] is False
    assert result["error"] == "No files provided for analysis"
