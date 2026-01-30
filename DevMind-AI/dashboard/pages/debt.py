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

if __name__ == "__main__":
    show_tech_debt()
