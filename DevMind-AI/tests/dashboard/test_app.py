from unittest.mock import MagicMock, patch
import pytest

# We need to mock streamlit as it cannot run in headless test env easily without display
import sys
from types import ModuleType

st_mock = MagicMock()
sys.modules["streamlit"] = st_mock

# Now import the app
from dashboard import app

def test_get_user_repos():
    repos = app.get_user_repos()
    assert len(repos) == 3
    assert repos[0]["name"] == "frontend-app"

def test_get_action_items():
    items = app.get_action_items()
    assert len(items) == 1
    assert items[0]["severity"] == "🔴 CRITICAL"

@patch("dashboard.app.st")
def test_login_with_github(mock_st):
    # Setup session state as a real object or mock capable of attribute access if the code does that
    # The code does `st.session_state.authenticated = True`
    # The default MagicMock will handle attribute assignment, but we need to check it later.

    # In the code:
    # if "authenticated" not in st.session_state: ...
    # st.session_state.authenticated = True

    # If session_state is a dict in the test, it fails with AttributeError when doing .attr = value
    # We should use a mock that supports both dict access and attribute access, or match implementation.
    # Streamlit's session_state supports both.

    class SessionState(dict):
        def __getattr__(self, key):
            return self[key]
        def __setattr__(self, key, value):
            self[key] = value

    mock_st.session_state = SessionState()

    app.login_with_github()

    assert mock_st.session_state.authenticated is True
    assert mock_st.session_state.user_name == "DevMind User"
    mock_st.rerun.assert_called_once()
