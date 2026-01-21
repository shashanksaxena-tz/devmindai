"""Main Streamlit dashboard application."""
import streamlit as st
import os
import sys

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
if "user_name" not in st.session_state:
    st.session_state.user_name = "User"

def main():
    """Main dashboard entry point."""
    # Sidebar navigation
    with st.sidebar:
        st.title("🧠 DevMind AI")

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
            st.page_link("app.py", label="🏠 Overview", icon="🏠")
            st.page_link("pages/security.py", label="🔒 Security", icon="🔒")
            st.page_link("pages/reviews.py", label="📝 Code Reviews", icon="📝")
            st.page_link("pages/tests.py", label="🧪 Tests", icon="🧪")
            st.page_link("pages/debt.py", label="💰 Tech Debt", icon="💰")
            # st.page_link("pages/documentation.py", label="📚 Documentation", icon="📚")
            # st.page_link("pages/incidents.py", label="🚨 Incidents", icon="🚨")

            if st.button("Logout"):
                st.session_state.authenticated = False
                st.rerun()

        else:
            if st.button("🔐 Login with GitHub"):
                login_with_github()

    # Main content area
    if not st.session_state.authenticated:
        show_landing_page()
    else:
        show_overview()

def login_with_github():
    """Mock login."""
    st.session_state.authenticated = True
    st.session_state.user_name = "DevMind User"
    st.rerun()

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
