# DevMind AI Phase 12: Dashboard & GitHub App Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the unified Streamlit dashboard for visualization and team collaboration, plus the GitHub App for seamless developer workflow integration.

**Architecture:** Streamlit-based dashboard with real-time updates, multi-repo management, and interactive visualizations. GitHub App with webhook processing, PR commenting, and bot commands.

**Tech Stack:** Streamlit, Plotly, FastAPI webhooks, PyGitHub, WebSockets

**Prerequisites:** All agent phases (1-11) should be substantially complete

---

## Task 1: Streamlit Dashboard Foundation

**Files:**
- Create: `dashboard/app.py`
- Create: `dashboard/pages/home.py`
- Create: `dashboard/components/`
- Test: `tests/dashboard/test_app.py`

### Implementation Overview

```python
# dashboard/app.py
"""Main Streamlit dashboard application."""
import streamlit as st
from datetime import datetime

# Page config
st.set_page_config(
    page_title="DevMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_repo" not in st.session_state:
    st.session_state.current_repo = None


def main():
    """Main dashboard entry point."""
    # Sidebar navigation
    with st.sidebar:
        st.image("assets/logo.png", width=200)
        st.title("DevMind AI")

        if st.session_state.authenticated:
            st.write(f"👤 {st.session_state.get('user_name', 'User')}")

            # Repository selector
            repos = get_user_repos()
            selected_repo = st.selectbox(
                "Repository",
                options=repos,
                format_func=lambda r: r.get("name", r),
            )
            st.session_state.current_repo = selected_repo

            st.divider()

            # Navigation
            page = st.radio(
                "Navigation",
                options=[
                    "🏠 Overview",
                    "🔒 Security",
                    "📝 Code Reviews",
                    "🧪 Tests",
                    "💰 Tech Debt",
                    "📚 Documentation",
                    "🚨 Incidents",
                    "📊 Settings",
                ],
            )
        else:
            if st.button("🔐 Login with GitHub"):
                login_with_github()

    # Main content area
    if not st.session_state.authenticated:
        show_landing_page()
    else:
        if "Overview" in page:
            show_overview()
        elif "Security" in page:
            show_security()
        elif "Code Reviews" in page:
            show_code_reviews()
        elif "Tests" in page:
            show_tests()
        elif "Tech Debt" in page:
            show_tech_debt()
        elif "Documentation" in page:
            show_documentation()
        elif "Incidents" in page:
            show_incidents()
        elif "Settings" in page:
            show_settings()


def show_landing_page():
    """Show landing page for unauthenticated users."""
    st.title("🧠 DevMind AI")
    st.subheader("Your AI-Powered Development Platform")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Code Reviews", "Automated", "AI-Powered")
    with col2:
        st.metric("Security Scans", "Continuous", "Real-time")
    with col3:
        st.metric("Test Generation", "Intelligent", "Edge Cases")


def show_overview():
    """Show overview dashboard."""
    st.title("📊 Organization Overview")

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Code Health", "82%", "+3%")
    with col2:
        st.metric("Security Score", "94%", "+7%")
    with col3:
        st.metric("Tech Debt", "$34K", "-12%")
    with col4:
        st.metric("Coverage", "76%", "+5%")

    # Action items
    st.subheader("🚨 Action Required")
    action_items = get_action_items()
    for item in action_items:
        with st.expander(f"{item['severity']} | {item['repo']} | {item['title']}"):
            st.write(item['description'])
            col1, col2 = st.columns(2)
            with col1:
                st.button("View Details", key=f"view_{item['id']}")
            with col2:
                st.button("Auto-fix", key=f"fix_{item['id']}")


def get_user_repos():
    """Fetch user's connected repositories."""
    # TODO: Fetch from API
    return [
        {"id": "1", "name": "frontend-app"},
        {"id": "2", "name": "api-server"},
        {"id": "3", "name": "mobile-app"},
    ]


def get_action_items():
    """Fetch action items."""
    # TODO: Fetch from API
    return [
        {
            "id": "1",
            "severity": "🔴 CRITICAL",
            "repo": "frontend-app",
            "title": "2 security vulnerabilities (axios)",
            "description": "CVE-2024-1234 affecting axios 0.21.1",
        },
    ]


if __name__ == "__main__":
    main()
```

---

## Task 2: Dashboard Pages (Security, Reviews, Debt)

**Files:**
- Create: `dashboard/pages/security.py`
- Create: `dashboard/pages/reviews.py`
- Create: `dashboard/pages/debt.py`
- Create: `dashboard/pages/tests.py`

### Implementation Overview

```python
# dashboard/pages/security.py
"""Security dashboard page."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def show_security():
    """Show security dashboard."""
    st.title("🔒 Security Dashboard")

    repo = st.session_state.get("current_repo", {})
    repo_name = repo.get("name", "Repository")

    # Security score gauge
    col1, col2 = st.columns([1, 2])
    with col1:
        score = 94
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Security Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "green" if score > 80 else "orange"},
                "steps": [
                    {"range": [0, 60], "color": "red"},
                    {"range": [60, 80], "color": "yellow"},
                    {"range": [80, 100], "color": "green"},
                ],
            },
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Vulnerability summary
        st.subheader("Vulnerabilities")
        cols = st.columns(4)
        with cols[0]:
            st.metric("🔴 Critical", "0")
        with cols[1]:
            st.metric("🟠 High", "2")
        with cols[2]:
            st.metric("🟡 Medium", "7")
        with cols[3]:
            st.metric("🟢 Low", "12")

    # Vulnerability list
    st.subheader("Actionable Vulnerabilities")

    vulnerabilities = get_vulnerabilities()
    for vuln in vulnerabilities:
        exploitable_badge = "⚠️ EXPLOITABLE" if vuln['exploitable'] else "✅ Not Exploitable"

        with st.expander(
            f"{vuln['severity']} | {vuln['cve']} | {vuln['package']} | {exploitable_badge}"
        ):
            st.write(f"**Description:** {vuln['description']}")
            st.write(f"**CVSS Score:** {vuln['cvss']}")
            st.write(f"**Fix:** Upgrade to {vuln['fix_version']}")

            if vuln['exploitable']:
                st.warning(f"**Exploitability Analysis:** {vuln['exploit_path']}")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔧 Auto-fix PR", key=f"fix_{vuln['id']}"):
                    trigger_auto_fix(vuln)
            with col2:
                if st.button("📋 View Details", key=f"details_{vuln['id']}"):
                    pass
            with col3:
                if st.button("⏰ Snooze 30 days", key=f"snooze_{vuln['id']}"):
                    pass

    # Trend chart
    st.subheader("Vulnerability Trend")
    dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
    values = [15 + (i % 5) for i in range(30)]

    fig = px.line(
        x=dates,
        y=values,
        labels={"x": "Date", "y": "Open Vulnerabilities"},
    )
    st.plotly_chart(fig, use_container_width=True)


def get_vulnerabilities():
    """Fetch vulnerabilities from API."""
    return [
        {
            "id": "1",
            "severity": "🟠 HIGH",
            "cve": "CVE-2024-5678",
            "package": "axios 0.21.1",
            "description": "Server-Side Request Forgery (SSRF)",
            "cvss": 7.4,
            "fix_version": "1.6.0",
            "exploitable": True,
            "exploit_path": "User input reaches axios.get() in src/api/proxy.js:47",
        },
        {
            "id": "2",
            "severity": "🟡 MEDIUM",
            "cve": "CVE-2024-1234",
            "package": "lodash 4.17.20",
            "description": "Prototype Pollution",
            "cvss": 5.3,
            "fix_version": "4.17.21",
            "exploitable": False,
            "exploit_path": None,
        },
    ]


def trigger_auto_fix(vuln):
    """Trigger auto-fix PR creation."""
    st.success(f"Creating PR to fix {vuln['cve']}...")
```

```python
# dashboard/pages/debt.py
"""Technical debt dashboard page."""
import streamlit as st
import plotly.express as px


def show_tech_debt():
    """Show technical debt dashboard."""
    st.title("💰 Technical Debt")

    # Overall metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Debt", "$34,000", "-$4,500")
    with col2:
        st.metric("Health Score", "72/100", "+8")
    with col3:
        st.metric("Open Issues", "47", "-12")

    # Debt breakdown
    st.subheader("Debt by Category")

    categories = ["Complexity", "Duplication", "Missing Tests", "Outdated Deps", "Code Smells"]
    values = [35, 20, 25, 15, 5]

    fig = px.pie(
        names=categories,
        values=values,
        title="Debt Distribution",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top refactoring priorities
    st.subheader("🎯 Top Refactoring Priorities")

    priorities = [
        {
            "file": "src/utils/parser.js",
            "issue": "Complexity 47",
            "suggestion": "Split into 3 smaller functions",
            "effort": "4 hours",
        },
        {
            "file": "src/api/*.js",
            "issue": "340 lines duplicated",
            "suggestion": "Extract shared API helper",
            "effort": "2 hours",
        },
    ]

    for i, item in enumerate(priorities, 1):
        with st.expander(f"{i}. {item['file']} - {item['issue']}"):
            st.write(f"**Suggestion:** {item['suggestion']}")
            st.write(f"**Estimated Effort:** {item['effort']}")
            st.button("Create Refactoring PR", key=f"refactor_{i}")
```

---

## Task 3: GitHub App Webhook Handler

**Files:**
- Create: `src/integrations/github/app.py`
- Create: `src/integrations/github/webhooks.py`
- Create: `src/integrations/github/commands.py`
- Test: `tests/integrations/test_github_app.py`

### Implementation Overview

```python
# src/integrations/github/webhooks.py
"""GitHub webhook handlers."""
from __future__ import annotations

import hmac
import hashlib
from typing import Any
from fastapi import HTTPException


class GitHubWebhookHandler:
    """Handles GitHub webhooks."""

    def __init__(self, webhook_secret: str, agent_orchestrator: Any):
        self.secret = webhook_secret
        self.orchestrator = agent_orchestrator

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature."""
        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    async def handle_webhook(self, event_type: str, payload: dict) -> dict:
        """Route webhook to appropriate handler."""
        handlers = {
            "pull_request": self._handle_pull_request,
            "pull_request_review_comment": self._handle_pr_comment,
            "issue_comment": self._handle_issue_comment,
            "push": self._handle_push,
            "installation": self._handle_installation,
        }

        handler = handlers.get(event_type)
        if not handler:
            return {"status": "ignored", "event": event_type}

        return await handler(payload)

    async def _handle_pull_request(self, payload: dict) -> dict:
        """Handle PR events (opened, synchronize)."""
        action = payload.get("action")
        if action not in ["opened", "synchronize"]:
            return {"status": "ignored", "action": action}

        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})

        # Trigger code review
        review_result = await self.orchestrator.trigger_review(
            repo_full_name=repo.get("full_name"),
            pr_number=pr.get("number"),
            head_sha=pr.get("head", {}).get("sha"),
        )

        # Trigger security scan
        security_result = await self.orchestrator.trigger_security_scan(
            repo_full_name=repo.get("full_name"),
            pr_number=pr.get("number"),
        )

        return {
            "status": "processed",
            "review_job": review_result.get("job_id"),
            "security_job": security_result.get("job_id"),
        }

    async def _handle_issue_comment(self, payload: dict) -> dict:
        """Handle issue/PR comments for bot commands."""
        comment = payload.get("comment", {})
        body = comment.get("body", "")

        # Check for bot mention
        if "@devmind" not in body.lower():
            return {"status": "ignored", "reason": "no mention"}

        # Parse command
        command = self._parse_command(body)
        if not command:
            return {"status": "ignored", "reason": "no command"}

        # Execute command
        return await self._execute_command(command, payload)

    def _parse_command(self, body: str) -> dict | None:
        """Parse bot command from comment."""
        import re

        patterns = [
            (r"@devmind\s+review", {"action": "review"}),
            (r"@devmind\s+security", {"action": "security"}),
            (r"@devmind\s+generate-tests", {"action": "generate_tests"}),
            (r"@devmind\s+explain", {"action": "explain"}),
            (r"@devmind\s+optimize", {"action": "optimize"}),
            (r"@devmind\s+docs", {"action": "docs"}),
            (r"@devmind\s+fix\s+(.+)", {"action": "fix", "target": 1}),
        ]

        for pattern, command in patterns:
            match = re.search(pattern, body.lower())
            if match:
                if "target" in command:
                    command["target"] = match.group(command["target"])
                return command

        return None

    async def _execute_command(self, command: dict, payload: dict) -> dict:
        """Execute a bot command."""
        action = command.get("action")
        repo = payload.get("repository", {})
        issue = payload.get("issue", {})

        if action == "review":
            result = await self.orchestrator.trigger_review(
                repo_full_name=repo.get("full_name"),
                pr_number=issue.get("number"),
            )
        elif action == "security":
            result = await self.orchestrator.trigger_security_scan(
                repo_full_name=repo.get("full_name"),
            )
        elif action == "generate_tests":
            result = await self.orchestrator.trigger_test_generation(
                repo_full_name=repo.get("full_name"),
                pr_number=issue.get("number"),
            )
        else:
            result = {"status": "unknown_command"}

        return {"status": "executed", "command": action, "result": result}

    async def _handle_push(self, payload: dict) -> dict:
        """Handle push events for main branch."""
        ref = payload.get("ref", "")
        if ref not in ["refs/heads/main", "refs/heads/master"]:
            return {"status": "ignored", "ref": ref}

        repo = payload.get("repository", {})

        # Trigger full analysis on main branch push
        await self.orchestrator.trigger_full_analysis(
            repo_full_name=repo.get("full_name"),
        )

        return {"status": "analysis_triggered"}

    async def _handle_installation(self, payload: dict) -> dict:
        """Handle app installation events."""
        action = payload.get("action")
        installation = payload.get("installation", {})

        if action == "created":
            # New installation
            repos = payload.get("repositories", [])
            await self.orchestrator.setup_repositories(
                installation_id=installation.get("id"),
                repositories=repos,
            )

        return {"status": "processed", "action": action}
```

---

## Task 4: GitHub PR Commenter

**Files:**
- Create: `src/integrations/github/commenter.py`
- Test: `tests/integrations/test_commenter.py`

### Implementation Overview

```python
# src/integrations/github/commenter.py
"""GitHub PR commenting functionality."""
from __future__ import annotations

from typing import Any
from github import Github, GithubException


class GitHubCommenter:
    """Posts comments to GitHub PRs."""

    def __init__(self, app_client: Github):
        self.github = app_client

    async def post_review_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        review_summary: dict,
    ) -> str:
        """Post review summary as PR comment."""
        repo = self.github.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        body = self._format_review_comment(review_summary)

        comment = pr.create_issue_comment(body)
        return comment.html_url

    async def post_inline_comments(
        self,
        repo_full_name: str,
        pr_number: int,
        comments: list[dict],
        commit_sha: str,
    ) -> int:
        """Post inline review comments."""
        repo = self.github.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        posted_count = 0
        for comment in comments:
            try:
                pr.create_review_comment(
                    body=self._format_inline_comment(comment),
                    commit=repo.get_commit(commit_sha),
                    path=comment["file_path"],
                    line=comment["line_number"],
                )
                posted_count += 1
            except GithubException as e:
                # Log error but continue
                pass

        return posted_count

    async def create_check_run(
        self,
        repo_full_name: str,
        head_sha: str,
        name: str,
        conclusion: str,
        summary: str,
    ) -> str:
        """Create a GitHub Check Run."""
        repo = self.github.get_repo(repo_full_name)

        check_run = repo.create_check_run(
            name=name,
            head_sha=head_sha,
            status="completed",
            conclusion=conclusion,
            output={
                "title": name,
                "summary": summary,
            },
        )

        return check_run.html_url

    def _format_review_comment(self, review: dict) -> str:
        """Format review as markdown comment."""
        blockers = review.get("blocker_count", 0)
        warnings = review.get("warning_count", 0)
        suggestions = review.get("suggestion_count", 0)

        verdict = "✅ Approved" if blockers == 0 else "❌ Changes Requested"

        return f"""## 🤖 DevMind Code Review

{verdict}

### Summary
| Category | Count |
|----------|-------|
| 🔴 Blocker | {blockers} |
| 🟠 Warning | {warnings} |
| 🟡 Suggestion | {suggestions} |

{review.get('summary', '')}

---
*Generated by [DevMind AI](https://devmind.ai)*
"""

    def _format_inline_comment(self, comment: dict) -> str:
        """Format inline comment."""
        severity_icons = {
            "blocker": "🔴",
            "warning": "🟠",
            "suggestion": "🟡",
            "nit": "💡",
        }

        icon = severity_icons.get(comment.get("severity", ""), "")
        title = comment.get("title", "Issue")
        message = comment.get("message", "")
        suggestion = comment.get("suggestion", "")

        body = f"{icon} **{title}**\n\n{message}"

        if suggestion:
            body += f"\n\n💡 **Suggestion:**\n```suggestion\n{suggestion}\n```"

        return body
```

---

## Task 5: Real-time Updates (WebSocket)

**Files:**
- Create: `src/api/websocket.py`
- Create: `dashboard/components/realtime.py`
- Test: `tests/api/test_websocket.py`

### Implementation Overview

```python
# src/api/websocket.py
"""WebSocket endpoints for real-time updates."""
from __future__ import annotations

import asyncio
import json
from typing import Any
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str):
        """Accept and register a new connection."""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove a connection."""
        if channel in self.active_connections:
            self.active_connections[channel].remove(websocket)

    async def broadcast(self, channel: str, message: dict):
        """Broadcast message to all connections in a channel."""
        if channel not in self.active_connections:
            return

        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, repo_id: str):
    """WebSocket endpoint for repo updates."""
    channel = f"repo:{repo_id}"
    await manager.connect(websocket, channel)

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Handle ping/pong or commands
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


async def notify_scan_complete(repo_id: str, scan_type: str, results: dict):
    """Notify connected clients of scan completion."""
    await manager.broadcast(
        f"repo:{repo_id}",
        {
            "type": "scan_complete",
            "scan_type": scan_type,
            "results": results,
        },
    )


async def notify_review_complete(repo_id: str, pr_number: int, review: dict):
    """Notify connected clients of review completion."""
    await manager.broadcast(
        f"repo:{repo_id}",
        {
            "type": "review_complete",
            "pr_number": pr_number,
            "summary": review,
        },
    )
```

---

## Summary

Phase 12 (Dashboard & GitHub App) consists of 5 tasks:

1. **Streamlit Dashboard Foundation** - Main app structure, navigation, auth
2. **Dashboard Pages** - Security, Reviews, Debt, Tests visualizations
3. **GitHub Webhook Handler** - Process GitHub events, route to agents
4. **GitHub PR Commenter** - Post reviews, inline comments, check runs
5. **Real-time Updates** - WebSocket for live dashboard updates

**Estimated Implementation Time:** ~2-3 weeks

**Dependencies:** All agent phases (1-11) should be complete
