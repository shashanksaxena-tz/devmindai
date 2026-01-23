"""DevMind AI Dashboard - Main Streamlit Application."""

import os
from datetime import datetime, timedelta

import httpx
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="DevMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .status-healthy {
        color: #4CAF50;
        font-weight: bold;
    }
    .status-warning {
        color: #FF9800;
        font-weight: bold;
    }
    .status-critical {
        color: #F44336;
        font-weight: bold;
    }
    .agent-card {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# API Client Functions
# =============================================================================

def api_request(method: str, endpoint: str, **kwargs) -> dict | None:
    """Make an API request to the DevMind backend."""
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.request(method, f"{API_URL}{endpoint}", **kwargs)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        st.error(f"API Error: {e}")
        return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None


def check_api_health() -> bool:
    """Check if the API is healthy."""
    result = api_request("GET", "/health")
    return result is not None and result.get("status") == "healthy"


# =============================================================================
# Sidebar Navigation
# =============================================================================

def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        st.markdown("# 🧠 DevMind AI")
        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigation",
            [
                "🏠 Overview",
                "📊 Repositories",
                "🔒 Security",
                "📝 Code Reviews",
                "🧪 Test Generation",
                "📈 Technical Debt",
                "🚨 Incidents",
                "📄 Documentation",
                "⚙️ Settings",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # API Status
        if check_api_health():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")

        # Version info
        st.markdown("---")
        st.caption("DevMind AI v0.1.0")

        return page


# =============================================================================
# Page: Overview Dashboard
# =============================================================================

def render_overview():
    """Render the main overview dashboard."""
    st.markdown('<p class="main-header">Welcome to DevMind AI</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">AI-powered developer platform with 10 intelligent agents</p>',
        unsafe_allow_html=True
    )

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Connected Repos",
            value="12",
            delta="+2 this week",
        )

    with col2:
        st.metric(
            label="Security Score",
            value="94%",
            delta="+7%",
        )

    with col3:
        st.metric(
            label="Tech Debt",
            value="$24K",
            delta="-12%",
            delta_color="inverse",
        )

    with col4:
        st.metric(
            label="Test Coverage",
            value="76%",
            delta="+5%",
        )

    st.markdown("---")

    # Agent Status Grid
    st.subheader("🤖 Agent Status")

    agents = [
        ("VulnScanner", "Security vulnerability scanning", "🔒", "healthy"),
        ("CodeReviewer", "Automated PR reviews", "📝", "healthy"),
        ("TestGenerator", "AI test generation", "🧪", "healthy"),
        ("DebtAnalyzer", "Technical debt analysis", "📊", "healthy"),
        ("DocGenerator", "API documentation", "📄", "healthy"),
        ("IncidentResponder", "Incident triage", "🚨", "healthy"),
        ("CodeMigrator", "Framework migrations", "🔄", "idle"),
        ("QueryOptimizer", "SQL optimization", "⚡", "healthy"),
        ("ADRRecorder", "Architecture decisions", "📋", "healthy"),
        ("PipelineGenerator", "CI/CD pipelines", "🔧", "healthy"),
    ]

    cols = st.columns(5)
    for i, (name, desc, icon, status) in enumerate(agents):
        with cols[i % 5]:
            status_color = "🟢" if status == "healthy" else "🟡" if status == "idle" else "🔴"
            st.markdown(f"""
            <div class="agent-card">
                <div style="font-size: 2rem; text-align: center;">{icon}</div>
                <div style="font-weight: bold; text-align: center;">{name}</div>
                <div style="font-size: 0.8rem; color: #666; text-align: center;">{desc}</div>
                <div style="text-align: center; margin-top: 0.5rem;">{status_color} {status.title()}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Activity Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Agent Activity (Last 7 Days)")

        # Sample data
        dates = [(datetime.now() - timedelta(days=i)).strftime("%m/%d") for i in range(6, -1, -1)]
        activity_data = {
            "Date": dates,
            "Code Reviews": [12, 15, 8, 22, 18, 14, 20],
            "Security Scans": [5, 8, 4, 7, 6, 9, 5],
            "Test Generations": [3, 5, 2, 7, 4, 3, 6],
        }

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=activity_data["Code Reviews"],
                                 mode='lines+markers', name='Code Reviews',
                                 line=dict(color='#1E88E5', width=2)))
        fig.add_trace(go.Scatter(x=dates, y=activity_data["Security Scans"],
                                 mode='lines+markers', name='Security Scans',
                                 line=dict(color='#E53935', width=2)))
        fig.add_trace(go.Scatter(x=dates, y=activity_data["Test Generations"],
                                 mode='lines+markers', name='Test Gen',
                                 line=dict(color='#43A047', width=2)))

        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis_title="",
            yaxis_title="Tasks",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🎯 Issues by Category")

        categories = ["Security", "Performance", "Style", "Testing", "Docs"]
        values = [8, 15, 23, 12, 5]
        colors = ["#E53935", "#FF9800", "#1E88E5", "#43A047", "#9C27B0"]

        fig = go.Figure(data=[go.Pie(
            labels=categories,
            values=values,
            hole=0.6,
            marker_colors=colors,
        )])
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            height=300,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Recent Activity
    st.subheader("🕒 Recent Activity")

    activities = [
        ("10 min ago", "CodeReviewer", "Completed review for PR #234 in frontend-app", "success"),
        ("25 min ago", "VulnScanner", "Found 2 vulnerabilities in api-server", "warning"),
        ("1 hour ago", "TestGenerator", "Generated 15 tests for payment module", "success"),
        ("2 hours ago", "DebtAnalyzer", "Debt score improved by 3% in core-lib", "success"),
        ("3 hours ago", "IncidentResponder", "Resolved incident INC-456", "success"),
    ]

    for time, agent, message, status in activities:
        icon = "✅" if status == "success" else "⚠️" if status == "warning" else "❌"
        st.markdown(f"**{time}** | {icon} **{agent}**: {message}")


# =============================================================================
# Page: Repositories
# =============================================================================

def render_repositories():
    """Render the repositories management page."""
    st.header("📊 Repositories")

    # Add repository button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Connect Repository", type="primary"):
            st.session_state.show_add_repo = True

    # Repository list
    repos = [
        {"name": "frontend-app", "language": "TypeScript", "health": 92, "vulns": 2, "coverage": 78},
        {"name": "api-server", "language": "Python", "health": 88, "vulns": 1, "coverage": 85},
        {"name": "mobile-app", "language": "React Native", "health": 75, "vulns": 5, "coverage": 45},
        {"name": "data-pipeline", "language": "Python", "health": 95, "vulns": 0, "coverage": 90},
        {"name": "auth-service", "language": "Go", "health": 91, "vulns": 0, "coverage": 82},
    ]

    for repo in repos:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])

            with col1:
                st.markdown(f"### 📁 {repo['name']}")
                st.caption(f"Language: {repo['language']}")

            with col2:
                health_color = "green" if repo['health'] >= 90 else "orange" if repo['health'] >= 70 else "red"
                st.metric("Health", f"{repo['health']}%")

            with col3:
                st.metric("Vulnerabilities", repo['vulns'],
                         delta=None if repo['vulns'] == 0 else f"-{repo['vulns']}" if repo['vulns'] < 3 else None,
                         delta_color="inverse")

            with col4:
                st.metric("Coverage", f"{repo['coverage']}%")

            with col5:
                if st.button("🔍 Analyze", key=f"analyze_{repo['name']}"):
                    st.info(f"Starting analysis for {repo['name']}...")

            st.markdown("---")


# =============================================================================
# Page: Security
# =============================================================================

def render_security():
    """Render the security dashboard page."""
    st.header("🔒 Security Dashboard")

    # Security score
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Overall Security Score", "94/100", "+7 this week")

    with col2:
        st.metric("Critical Vulnerabilities", "0", "0")

    with col3:
        st.metric("High Vulnerabilities", "2", "-3 this week", delta_color="inverse")

    st.markdown("---")

    # Vulnerability list
    st.subheader("🚨 Active Vulnerabilities")

    vulns = [
        {
            "cve": "CVE-2024-5678",
            "package": "axios@0.21.1",
            "severity": "High",
            "repo": "frontend-app",
            "exploitable": True,
            "fix": "Upgrade to axios@1.6.0",
        },
        {
            "cve": "CVE-2024-1234",
            "package": "lodash@4.17.15",
            "severity": "Medium",
            "repo": "api-server",
            "exploitable": False,
            "fix": "Upgrade to lodash@4.17.21",
        },
    ]

    for vuln in vulns:
        severity_color = "🔴" if vuln["severity"] == "Critical" else "🟠" if vuln["severity"] == "High" else "🟡"
        exploitable_badge = "⚠️ EXPLOITABLE" if vuln["exploitable"] else "✅ Not Exploitable"

        with st.expander(f"{severity_color} {vuln['cve']} | {vuln['package']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Repository:** {vuln['repo']}")
                st.markdown(f"**Severity:** {vuln['severity']}")
                st.markdown(f"**Status:** {exploitable_badge}")
            with col2:
                st.markdown(f"**Recommended Fix:** {vuln['fix']}")
                if st.button("🔧 Auto-fix PR", key=f"fix_{vuln['cve']}"):
                    st.success("Creating pull request with fix...")

    # Scan trigger
    st.markdown("---")
    st.subheader("🔄 Run Security Scan")

    repo = st.selectbox("Select Repository", ["All Repositories", "frontend-app", "api-server", "mobile-app"])
    if st.button("Start Scan", type="primary"):
        with st.spinner("Running security scan..."):
            st.success("Scan completed! No new vulnerabilities found.")


# =============================================================================
# Page: Code Reviews
# =============================================================================

def render_code_reviews():
    """Render the code reviews page."""
    st.header("📝 Code Reviews")

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Reviews Today", "12")
    with col2:
        st.metric("Avg Review Time", "2.3 min")
    with col3:
        st.metric("Issues Found", "47")
    with col4:
        st.metric("Blockers", "3")

    st.markdown("---")

    # Recent reviews
    st.subheader("Recent Reviews")

    reviews = [
        {"pr": "#234", "repo": "frontend-app", "status": "completed", "issues": 5, "time": "10 min ago"},
        {"pr": "#156", "repo": "api-server", "status": "completed", "issues": 2, "time": "1 hour ago"},
        {"pr": "#89", "repo": "mobile-app", "status": "in_progress", "issues": 0, "time": "Just now"},
    ]

    for review in reviews:
        status_icon = "✅" if review["status"] == "completed" else "🔄"
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

        with col1:
            st.markdown(f"**PR {review['pr']}** in {review['repo']}")
        with col2:
            st.markdown(f"{status_icon} {review['status'].title()}")
        with col3:
            st.markdown(f"🔍 {review['issues']} issues")
        with col4:
            st.markdown(f"🕒 {review['time']}")

    # Manual review
    st.markdown("---")
    st.subheader("🔍 Review Code")

    code = st.text_area("Paste code to review:", height=200, placeholder="Paste your code here...")
    if st.button("Review Code", type="primary"):
        if code:
            with st.spinner("Analyzing code..."):
                st.success("Review complete!")
                st.json({
                    "security": "No issues found",
                    "performance": "Consider caching this result",
                    "style": "Line 5: Consider using const instead of let",
                })


# =============================================================================
# Page: Test Generation
# =============================================================================

def render_test_generation():
    """Render the test generation page."""
    st.header("🧪 Test Generation")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Generate Tests")
        code = st.text_area("Source Code:", height=300, placeholder="Paste your source code here...")
        framework = st.selectbox("Test Framework", ["pytest", "jest", "vitest", "junit"])

        if st.button("Generate Tests", type="primary"):
            if code:
                with st.spinner("Generating tests..."):
                    st.success("Tests generated successfully!")

    with col2:
        st.subheader("Generated Tests")
        st.code("""
import pytest
from src.module import function_to_test

class TestFunctionToTest:
    def test_happy_path(self):
        result = function_to_test("valid_input")
        assert result is not None

    def test_edge_case_empty(self):
        with pytest.raises(ValueError):
            function_to_test("")

    def test_edge_case_none(self):
        with pytest.raises(TypeError):
            function_to_test(None)
        """, language="python")


# =============================================================================
# Page: Technical Debt
# =============================================================================

def render_technical_debt():
    """Render the technical debt analysis page."""
    st.header("📈 Technical Debt Analysis")

    # Overall metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Debt", "$24,000", "-12% this month", delta_color="inverse")

    with col2:
        st.metric("Health Score", "72/100", "+3 points")

    with col3:
        st.metric("Issues", "47", "-8 this week", delta_color="inverse")

    # Debt breakdown chart
    st.subheader("Debt by Category")

    categories = ["Code Duplication", "Complex Functions", "Missing Tests", "Outdated Deps", "Code Smells"]
    values = [8000, 6000, 5000, 3000, 2000]

    fig = go.Figure(data=[
        go.Bar(x=categories, y=values, marker_color=['#E53935', '#FF9800', '#1E88E5', '#43A047', '#9C27B0'])
    ])
    fig.update_layout(
        yaxis_title="Estimated Cost ($)",
        xaxis_title="",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top issues
    st.subheader("Top Refactoring Priorities")

    issues = [
        {"file": "src/utils/parser.js", "issue": "Complexity: 47 (split into 3 functions)", "cost": "$3,200"},
        {"file": "src/api/*.js", "issue": "340 lines duplicated (extract shared module)", "cost": "$2,800"},
        {"file": "tests/", "issue": "34% coverage (add 12 critical tests)", "cost": "$2,400"},
    ]

    for i, issue in enumerate(issues, 1):
        st.markdown(f"**{i}. {issue['file']}**")
        st.markdown(f"   {issue['issue']} | Est. fix cost: {issue['cost']}")


# =============================================================================
# Page: Incidents
# =============================================================================

def render_incidents():
    """Render the incidents page."""
    st.header("🚨 Incident Response")

    # Active incidents
    st.subheader("Active Incidents")

    incidents = [
        {"id": "INC-789", "title": "API latency spike", "severity": "P2", "status": "investigating", "time": "15 min"},
    ]

    if not incidents:
        st.success("No active incidents! 🎉")
    else:
        for inc in incidents:
            severity_color = "🔴" if inc["severity"] == "P1" else "🟠" if inc["severity"] == "P2" else "🟡"
            st.warning(f"{severity_color} **{inc['id']}**: {inc['title']} | Status: {inc['status']} | Duration: {inc['time']}")

    # Recent incidents
    st.markdown("---")
    st.subheader("Recent Incidents (Resolved)")

    resolved = [
        {"id": "INC-788", "title": "Database connection timeout", "resolved": "2 hours ago", "mttr": "23 min"},
        {"id": "INC-787", "title": "Memory leak in worker", "resolved": "Yesterday", "mttr": "45 min"},
        {"id": "INC-786", "title": "SSL certificate expiry", "resolved": "2 days ago", "mttr": "12 min"},
    ]

    for inc in resolved:
        st.markdown(f"✅ **{inc['id']}**: {inc['title']} | Resolved: {inc['resolved']} | MTTR: {inc['mttr']}")


# =============================================================================
# Page: Documentation
# =============================================================================

def render_documentation():
    """Render the documentation generation page."""
    st.header("📄 Documentation Generator")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Generate Documentation")
        doc_type = st.selectbox("Documentation Type", ["API Reference", "README", "Architecture", "Changelog"])
        repo = st.selectbox("Repository", ["frontend-app", "api-server", "mobile-app"])

        if st.button("Generate", type="primary"):
            with st.spinner("Generating documentation..."):
                st.success("Documentation generated!")

    with col2:
        st.subheader("Preview")
        st.markdown("""
        # API Reference

        ## Endpoints

        ### GET /api/users

        Returns a list of users.

        **Parameters:**
        - `limit` (optional): Number of results (default: 10)
        - `offset` (optional): Pagination offset

        **Response:**
        ```json
        {
          "users": [...],
          "total": 100
        }
        ```
        """)


# =============================================================================
# Page: Settings
# =============================================================================

def render_settings():
    """Render the settings page."""
    st.header("⚙️ Settings")

    tab1, tab2, tab3 = st.tabs(["General", "Integrations", "Notifications"])

    with tab1:
        st.subheader("General Settings")
        st.text_input("Organization Name", value="Acme Corp")
        st.selectbox("Default LLM", ["Claude (Recommended)", "Gemini", "GPT-4"])
        st.checkbox("Enable automatic PR reviews", value=True)
        st.checkbox("Enable security scanning on push", value=True)
        st.checkbox("Enable daily debt reports", value=False)

    with tab2:
        st.subheader("Integrations")
        st.markdown("### GitHub")
        st.text_input("GitHub App ID", type="password")
        st.text_input("Client ID", type="password")

        st.markdown("### Slack")
        st.text_input("Slack Webhook URL", type="password")

    with tab3:
        st.subheader("Notifications")
        st.multiselect(
            "Email notifications for:",
            ["Critical vulnerabilities", "PR reviews completed", "Incidents", "Weekly reports"],
            default=["Critical vulnerabilities", "Incidents"]
        )

    if st.button("Save Settings", type="primary"):
        st.success("Settings saved!")


# =============================================================================
# Main App
# =============================================================================

def main():
    """Main application entry point."""
    # Render sidebar and get current page
    page = render_sidebar()

    # Route to appropriate page
    if page == "🏠 Overview":
        render_overview()
    elif page == "📊 Repositories":
        render_repositories()
    elif page == "🔒 Security":
        render_security()
    elif page == "📝 Code Reviews":
        render_code_reviews()
    elif page == "🧪 Test Generation":
        render_test_generation()
    elif page == "📈 Technical Debt":
        render_technical_debt()
    elif page == "🚨 Incidents":
        render_incidents()
    elif page == "📄 Documentation":
        render_documentation()
    elif page == "⚙️ Settings":
        render_settings()


if __name__ == "__main__":
    main()
