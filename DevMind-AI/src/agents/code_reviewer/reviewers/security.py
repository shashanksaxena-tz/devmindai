# src/agents/code_reviewer/reviewers/security.py
"""Security-focused code reviewer."""
from __future__ import annotations

import time
from typing import Any, Optional

from .base import BaseReviewer, ReviewResult, ReviewComment, CommentSeverity


class SecurityReviewer(BaseReviewer):
    """Reviews code for security vulnerabilities."""

    name = "security"
    category = "security"
    description = "Scans for OWASP Top 10, injection, auth issues, secrets"

    SECURITY_PATTERNS = [
        "sql injection",
        "xss",
        "csrf",
        "hardcoded secret",
        "path traversal",
        "command injection",
        "insecure deserialization",
        "weak crypto",
        "missing auth",
        "sensitive data exposure",
    ]

    async def review(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ReviewResult:
        """Perform security review."""
        start_time = time.time()

        prompt = self._build_security_prompt(file_path, diff, full_content)

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a security expert reviewing code for vulnerabilities.",
            response_format={"type": "json_object"},
        )

        comments = self._parse_response(response, file_path)

        duration_ms = int((time.time() - start_time) * 1000)

        return ReviewResult(
            reviewer_name=self.name,
            comments=comments,
            duration_ms=duration_ms,
        )

    def _build_security_prompt(
        self,
        file_path: str,
        diff: str,
        full_content: str,
    ) -> str:
        """Build security-focused review prompt."""
        return f"""You are a security expert. Review this code for vulnerabilities.

File: {file_path}

Code changes (diff):
```
{diff}
```

Check for these security issues:
1. SQL Injection - string interpolation in queries
2. XSS - unescaped user input in HTML
3. Hardcoded Secrets - API keys, passwords in code
4. Command Injection - shell commands with user input
5. Path Traversal - file paths from user input
6. Insecure Deserialization - pickle, eval on user data
7. Missing Authentication - unprotected endpoints
8. Weak Cryptography - MD5, SHA1 for passwords
9. CSRF - missing tokens on state-changing operations
10. Sensitive Data Exposure - logging secrets, PII

For each vulnerability found, provide:
- type: vulnerability type (e.g., "sql_injection")
- severity: "blocker" for exploitable, "warning" for potential
- line: line number
- message: clear explanation of the risk
- fix: specific remediation code

Return JSON: {{"issues": [...]}}

Only report real issues. Avoid false positives.
"""
