"""Code review dashboard page."""
import streamlit as st
import plotly.express as px

def show_code_reviews():
    """Show code reviews dashboard."""
    st.title("📝 Code Reviews")

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Open PRs", "12", "+2")
    with col2:
        st.metric("Avg Review Time", "4h 23m", "-15m")
    with col3:
        st.metric("Auto-Approval Rate", "45%", "+5%")

    # Recent Reviews
    st.subheader("Recent Reviews")

    reviews = [
        {
            "id": 123,
            "title": "feat: Add new user profile",
            "author": "jdoe",
            "status": "Changes Requested",
            "blockers": 1,
            "warnings": 3,
            "suggestions": 5
        },
        {
            "id": 124,
            "title": "fix: Database connection timeout",
            "author": "msmith",
            "status": "Approved",
            "blockers": 0,
            "warnings": 0,
            "suggestions": 2
        }
    ]

    for review in reviews:
        with st.expander(f"#{review['id']} {review['title']} - {review['status']}"):
            st.write(f"**Author:** {review['author']}")

            c1, c2, c3 = st.columns(3)
            c1.metric("Blockers", review["blockers"])
            c2.metric("Warnings", review["warnings"])
            c3.metric("Suggestions", review["suggestions"])

            st.button("View Full Report", key=f"review_btn_{review['id']}")

if __name__ == "__main__":
    show_code_reviews()
