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

if __name__ == "__main__":
    show_security()
