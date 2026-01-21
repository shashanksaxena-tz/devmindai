"""Tests dashboard page."""
import streamlit as st
import plotly.express as px

def show_tests():
    """Show tests dashboard."""
    st.title("🧪 Tests & Coverage")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tests", "452", "+12")
    with col2:
        st.metric("Pass Rate", "98.5%", "-0.2%")
    with col3:
        st.metric("Coverage", "84%", "+1%")
    with col4:
        st.metric("Flaky Tests", "3", "0")

    # Coverage Heatmap (Mock)
    st.subheader("Coverage Heatmap")

    # Mock data for heatmap
    data = [
        {"module": "api/auth", "coverage": 95},
        {"module": "api/users", "coverage": 88},
        {"module": "core/db", "coverage": 92},
        {"module": "utils/helpers", "coverage": 100},
        {"module": "integrations/stripe", "coverage": 65},
        {"module": "legacy/parser", "coverage": 45},
    ]

    fig = px.bar(
        data,
        x="module",
        y="coverage",
        color="coverage",
        range_y=[0, 100],
        color_continuous_scale=["red", "yellow", "green"],
        title="Module Coverage"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Generated Tests
    st.subheader("🤖 AI-Generated Tests")
    st.info("The following tests were automatically generated to cover edge cases.")

    generated_tests = [
        {
            "file": "tests/api/test_users.py",
            "function": "test_create_user_invalid_email_unicode",
            "reason": "Edge case detection: Unicode handling in email regex"
        },
        {
            "file": "tests/utils/test_helpers.py",
            "function": "test_format_date_leap_year",
            "reason": "Missing branch coverage for leap years"
        }
    ]

    for test in generated_tests:
        with st.expander(f"{test['function']} ({test['file']})"):
            st.write(f"**Reason:** {test['reason']}")
            st.code("def test_create_user_invalid_email_unicode():\n    ...", language="python")
            st.button("Review & Merge", key=f"merge_{test['function']}")

if __name__ == "__main__":
    show_tests()
