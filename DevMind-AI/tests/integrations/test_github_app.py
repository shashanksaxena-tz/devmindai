import pytest
from unittest.mock import AsyncMock, MagicMock
from src.integrations.github.webhooks import GitHubWebhookHandler

@pytest.mark.asyncio
async def test_webhook_verify_signature():
    handler = GitHubWebhookHandler("secret", MagicMock())
    payload = b"payload"
    # calculated sha256 of "payload" with key "secret"
    # echo -n "payload" | openssl dgst -sha256 -hmac "secret"
    # (checking locally or trusting logic)
    import hmac, hashlib
    expected = hmac.new(b"secret", payload, hashlib.sha256).hexdigest()
    signature = f"sha256={expected}"

    assert handler.verify_signature(payload, signature) is True
    assert handler.verify_signature(payload, "sha256=wrong") is False

@pytest.mark.asyncio
async def test_handle_pull_request_opened():
    orchestrator = AsyncMock()
    orchestrator.trigger_review.return_value = {"job_id": "review_123"}
    orchestrator.trigger_security_scan.return_value = {"job_id": "sec_123"}

    handler = GitHubWebhookHandler("secret", orchestrator)

    payload = {
        "action": "opened",
        "pull_request": {"number": 1, "head": {"sha": "abc"}},
        "repository": {"full_name": "owner/repo"}
    }

    result = await handler.handle_webhook("pull_request", payload)

    assert result["status"] == "processed"
    orchestrator.trigger_review.assert_called_once()
    orchestrator.trigger_security_scan.assert_called_once()

@pytest.mark.asyncio
async def test_handle_issue_comment_command():
    orchestrator = AsyncMock()
    orchestrator.trigger_review.return_value = {"status": "ok"}

    handler = GitHubWebhookHandler("secret", orchestrator)

    payload = {
        "action": "created",
        "comment": {"body": "Please @devmind review this"},
        "issue": {"number": 2},
        "repository": {"full_name": "owner/repo"}
    }

    result = await handler.handle_webhook("issue_comment", payload)

    assert result["status"] == "executed"
    assert result["command"] == "review"
    orchestrator.trigger_review.assert_called_once()
