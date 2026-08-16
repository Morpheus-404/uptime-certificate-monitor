import json
import pytest
from urllib.error import HTTPError, URLError
from unittest.mock import MagicMock, patch

from monitor.checks import CHECK_TIMEOUT_SECONDS, CheckResult
from monitor.notifier import build_failure_message, send_discord_notification


def test_build_failure_message_returns_formatted_message() -> None:
    failed_results = [
        CheckResult(success=False, message="HTTP failed"),
        CheckResult(success=False, message="SSL failed"),
    ]
    expected_message = (
        "Monitoring checks failed:\n"
        "- HTTP failed\n"
        "- SSL failed"
    )

    assert build_failure_message(failed_results) == expected_message


def test_send_discord_notification_sends_post_request() -> None:
    response = MagicMock()
    response.__enter__.return_value = response

    with patch(
        "monitor.notifier.urllib.request.urlopen",
        return_value=response,
    ) as mock_urlopen:

        send_discord_notification(
            "https://discord.example.com/webhook",
            "Test message",
        )

    request = mock_urlopen.call_args.args[0]

    assert request.full_url == "https://discord.example.com/webhook"
    assert request.get_method() == "POST"
    assert request.get_header("Content-type") == "application/json"
    assert request.get_header("User-agent") == "uptime-certificate-monitor/0.1"
    assert request.data == json.dumps(
        {"content": "Test message"}
    ).encode("utf-8")
    assert (
        mock_urlopen.call_args.kwargs["timeout"] == CHECK_TIMEOUT_SECONDS
    )


def test_send_discord_notification_handles_http_error() -> None:
    with (
        patch(
            "monitor.notifier.urllib.request.urlopen",
            side_effect=HTTPError(
                url="https://discord.example.com/webhook",
                code=400,
                msg="Bad Request",
                hdrs={},
                fp=None,
            ),
        ),
        patch(
            "monitor.notifier.logger.error",
        ) as mock_logger,
    ):
        send_discord_notification(
            "https://discord.example.com/webhook",
            "Test message",
        )

    mock_logger.assert_called_once_with(
        "Discord notification failed with HTTP status %s: %s",
        400,
        "Bad Request",
    )


def test_send_discord_notification_handles_url_error() -> None:
    with (
        patch(
            "monitor.notifier.urllib.request.urlopen",
            side_effect=URLError(
                reason="Connection refused",
            ),
        ),
        patch(
            "monitor.notifier.logger.error",
        ) as mock_logger,
    ):
        send_discord_notification(
            "https://discord.example.com/webhook",
            "Test message",
        )

    mock_logger.assert_called_once_with(
        "Discord notification failed: %s",
        "Connection refused",
    )
