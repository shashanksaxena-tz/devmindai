"""Transforms code for migration."""
from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Any, Optional

from .scanner import MigrationTarget


@dataclass
class TransformResult:
    """Result of code transformation."""
    file_path: str
    original_code: str
    transformed_code: str
    success: bool
    error: Optional[str] = None
    diff: str = ""


class CodeTransformer:
    """Transforms code using LLM."""

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    async def transform(
        self,
        target: MigrationTarget,
        full_file_content: str,
        migration_type: str,
        target_version: str,
    ) -> TransformResult:
        """Transform a migration target."""
        prompt = f"""Transform this code from {migration_type} to {target_version}:

Original code:
```
{target.current_code}
```

Full file context:
```
{full_file_content[:2000]}
```

Requirements:
1. Preserve all functionality
2. Follow {target_version} best practices
3. Maintain code style consistency

Return only the transformed code, no explanations.
"""

        try:
            transformed = await self.llm_client.generate(
                prompt=prompt,
                system=f"You are an expert at {migration_type} migrations.",
            )

            # Basic cleanup if LLM returns markdown code blocks
            if isinstance(transformed, str):
                if transformed.startswith("```"):
                     # Remove first line (```language) and last line (```)
                     lines = transformed.splitlines()
                     if len(lines) >= 2:
                         if lines[0].startswith("```"):
                             lines = lines[1:]
                         if lines[-1].strip() == "```":
                             lines = lines[:-1]
                         transformed = "\n".join(lines)

            return TransformResult(
                file_path=target.file_path,
                original_code=target.current_code,
                transformed_code=transformed,
                success=True,
                diff=self._generate_diff(target.current_code, transformed),
            )

        except Exception as e:
            return TransformResult(
                file_path=target.file_path,
                original_code=target.current_code,
                transformed_code="",
                success=False,
                error=str(e),
            )

    def _generate_diff(self, original: str, transformed: str) -> str:
        """Generate unified diff."""
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            transformed.splitlines(keepends=True),
            fromfile="original",
            tofile="transformed",
        )
        return "".join(diff)
