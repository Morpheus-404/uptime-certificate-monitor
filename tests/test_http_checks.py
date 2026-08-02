from unittest.mock import patch
from urllib.error import HTTPError, URLError

from monitor.config import HttpCheckConfig
from monitor.checks import run_http_check, CHECK_TIMEOUT_SECONDS


class FakeResponse:
    def __init__(self, status: int):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return None



def test_run_http_check_returns_success_for_status_200() -> None:
    config = HttpCheckConfig(url="https://example.com")

    with patch(
        "monitor.checks.urllib.request.urlopen",
        return_value=FakeResponse(200),
    ):
        result = run_http_check(config)

    assert result.success is True
    assert result.message == "HTTP status for https://example.com: 200"


def test_run_http_check_returns_failure_for_status_500() -> None:
    config = HttpCheckConfig(url="https://example.com")

    error = HTTPError(
        url="https://example.com",
        code=500,
        msg="Internal Server Error",
        hdrs=None,
        fp=None
    )

    with patch(
        "monitor.checks.urllib.request.urlopen",
         side_effect=error
    ):
        result = run_http_check(config)

    assert result.success is False
    assert result.message == (
        f"HTTP check failed for {config.url}: "
        f"status {error.code}: {error.reason}"
    )


def test_run_http_check_returns_failure_for_url_error() -> None:
    config = HttpCheckConfig(url="https://example.com")

    error = URLError(
        reason="Name or service not known"
    )

    with patch(
        "monitor.checks.urllib.request.urlopen",
        side_effect=error
    ):
        result = run_http_check(config)

    assert result.success is False
    assert result.message == (
        f"HTTP check failed for {config.url}: "
        f"{error.reason}"
    )


def test_run_http_check_returns_failure_for_blank_url() -> None:
    config = HttpCheckConfig(url="    ")
    result = run_http_check(config)

    assert result.success is False
    assert result.message == "HTTP check failed: URL is empty"


def test_run_http_check_strips_whitespace_from_url() -> None:
    config = HttpCheckConfig(url="   https://example.com   ")

    with patch(
        "monitor.checks.urllib.request.urlopen",
        return_value=FakeResponse(200),
    ) as mock_urlopen:

        run_http_check(config)

        mock_urlopen.assert_called_once_with(
            "https://example.com",
            timeout=CHECK_TIMEOUT_SECONDS,
        )
