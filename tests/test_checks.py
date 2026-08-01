from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError
from datetime import datetime, UTC, timedelta

from monitor.checks import CHECK_TIMEOUT_SECONDS, run_http_check, run_ssl_check, CheckResult
from monitor.config import HttpCheckConfig, SslCheckConfig

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


def test_run_ssl_check_returns_success_for_valid_certificate() -> None:
    config = SslCheckConfig(hostname="example.com")

    certificate_expiration = (
        datetime.now(UTC) + timedelta(days=30, minutes=1)
    ).strftime("%b %d %H:%M:%S %Y %Z")

    connection = MagicMock()
    connection.__enter__.return_value = connection

    ssl_socket = MagicMock()
    ssl_socket.__enter__.return_value = ssl_socket
    ssl_socket.getpeercert.return_value = {
        "notAfter": certificate_expiration,
    }

    context = MagicMock()
    context.wrap_socket.return_value = ssl_socket

    with (
        patch(
            "monitor.checks.socket.create_connection",
            return_value=connection,
        ) as mock_create_connection,
        patch(
            "monitor.checks.ssl.create_default_context",
            return_value=context,
        ) as mock_create_default_context,
    ):
        result = run_ssl_check(config)

    assert result.success is True
    assert result.message == (
        "SSL certificate for example.com expires in 30 days"
    )

    mock_create_default_context.assert_called_once_with()

    mock_create_connection.assert_called_once_with(
        ("example.com", 443),
        timeout=CHECK_TIMEOUT_SECONDS,
    )

    context.wrap_socket.assert_called_once_with(
        connection,
        server_hostname="example.com",
    )

    ssl_socket.getpeercert.assert_called_once_with()


def test_run_ssl_check_returns_failure_for_expired_certificate() -> None:
    config = SslCheckConfig(hostname="example.com")

    certificate_expiration = (
        datetime.now(UTC) - timedelta(days=3) + timedelta(minutes=1)
    ).strftime("%b %d %H:%M:%S %Y %Z")

    connection = MagicMock()
    connection.__enter__.return_value = connection

    ssl_socket = MagicMock()
    ssl_socket.__enter__.return_value = ssl_socket
    ssl_socket.getpeercert.return_value = {
        "notAfter": certificate_expiration,
    }

    context = MagicMock()
    context.wrap_socket.return_value = ssl_socket

    with (
        patch(
            "monitor.checks.socket.create_connection",
            return_value=connection,
        ) as mock_create_connection,
        patch(
            "monitor.checks.ssl.create_default_context",
            return_value=context,
        ) as mock_create_default_context,
    ):
        result = run_ssl_check(config)

    assert result.success is False
    assert result.message == (
        "SSL certificate for example.com expired 3 days ago"
    )

    mock_create_default_context.assert_called_once_with()

    mock_create_connection.assert_called_once_with(
        ("example.com", 443),
        timeout=CHECK_TIMEOUT_SECONDS,
    )

    context.wrap_socket.assert_called_once_with(
        connection,
        server_hostname="example.com",
    )

    ssl_socket.getpeercert.assert_called_once_with()


def test_run_ssl_check_returns_failure_for_blank_hostname() -> None:
    config = SslCheckConfig(hostname="    ")

    result = run_ssl_check(config)

    assert result.success is False
    assert result.message == "SSL check failed: hostname is empty"


def test_run_ssl_check_returns_failure_for_connection_error() -> None:
    config = SslCheckConfig(hostname="example.com")

    with patch(
        "monitor.checks.socket.create_connection",
        side_effect=OSError("Connection refused"),
    ) as mock_create_connection:

        result = run_ssl_check(config)

    assert result.success is False
    assert result.message == (
        "SSL check failed for example.com: "
        "Connection refused"
    )

    mock_create_connection.assert_called_once_with(
        ("example.com", 443),
        timeout=CHECK_TIMEOUT_SECONDS,
    )


def test_run_ssl_check_returns_failure_for_missing_not_after() -> None:
    config = SslCheckConfig(hostname="example.com")

    connection = MagicMock()
    connection.__enter__.return_value = connection

    ssl_socket = MagicMock()
    ssl_socket.__enter__.return_value = ssl_socket
    ssl_socket.getpeercert.return_value = {}

    context = MagicMock()
    context.wrap_socket.return_value = ssl_socket

    with (
        patch(
            "monitor.checks.socket.create_connection",
            return_value=connection,
        ) as mock_create_connection,
        patch(
            "monitor.checks.ssl.create_default_context",
            return_value=context,
        ) as mock_create_default_context,
    ):
        result = run_ssl_check(config)

    assert result.success is False
    assert result.message == (
        "SSL certificate for example.com "
        "is missing the expiration date"
    )

    mock_create_default_context.assert_called_once_with()

    mock_create_connection.assert_called_once_with(
        ("example.com", 443),
        timeout=CHECK_TIMEOUT_SECONDS,
    )

    context.wrap_socket.assert_called_once_with(
        connection,
        server_hostname="example.com",
    )

    ssl_socket.getpeercert.assert_called_once_with()


def test_run_ssl_check_returns_failure_for_invalid_expiration_date() -> None:
    config = SslCheckConfig(hostname="example.com")

    connection = MagicMock()
    connection.__enter__.return_value = connection

    ssl_socket = MagicMock()
    ssl_socket.__enter__.return_value = ssl_socket
    ssl_socket.getpeercert.return_value = {
        "notAfter": "invalid date format",
    }

    context = MagicMock()
    context.wrap_socket.return_value = ssl_socket

    with (
        patch(
            "monitor.checks.socket.create_connection",
            return_value=connection,
        ) as mock_create_connection,
        patch(
            "monitor.checks.ssl.create_default_context",
            return_value=context,
        ) as mock_create_default_context,
    ):
        result = run_ssl_check(config)

    assert result.success is False
    assert result.message == (
        "SSL certificate for example.com "
        "has an invalid expiration date"
    )

    mock_create_default_context.assert_called_once_with()

    mock_create_connection.assert_called_once_with(
        ("example.com", 443),
        timeout=CHECK_TIMEOUT_SECONDS,
    )

    context.wrap_socket.assert_called_once_with(
        connection,
        server_hostname="example.com",
    )

    ssl_socket.getpeercert.assert_called_once_with()
