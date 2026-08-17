from collections.abc import Generator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from monitor.checks import run_ssl_check
from monitor.config import SslCheckConfig

TEST_TIMEOUT_SECONDS = 8.5


@dataclass
class SslTestEnvironment:
    connection: MagicMock
    ssl_socket: MagicMock
    context: MagicMock
    mock_create_connection: MagicMock
    mock_create_default_context: MagicMock


@pytest.fixture
def ssl_environment() -> Generator[SslTestEnvironment, None, None]:
    connection = MagicMock()
    connection.__enter__.return_value = connection

    ssl_socket = MagicMock()
    ssl_socket.__enter__.return_value = ssl_socket

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
        yield SslTestEnvironment(
            connection=connection,
            ssl_socket=ssl_socket,
            context=context,
            mock_create_connection=mock_create_connection,
            mock_create_default_context=mock_create_default_context,
        )


def assert_ssl_dependencies_called(
    ssl_environment: SslTestEnvironment,
    timeout: float,
    hostname: str = "example.com",
) -> None:
    ssl_environment.mock_create_default_context.assert_called_once_with()

    ssl_environment.mock_create_connection.assert_called_once_with(
        (hostname, 443),
        timeout=timeout,
    )

    ssl_environment.context.wrap_socket.assert_called_once_with(
        ssl_environment.connection,
        server_hostname=hostname,
    )

    ssl_environment.ssl_socket.getpeercert.assert_called_once_with()


def test_run_ssl_check_returns_success_for_valid_certificate(
    ssl_environment: SslTestEnvironment,
) -> None:
    config = SslCheckConfig(hostname="example.com")

    certificate_expiration = (
        datetime.now(UTC) + timedelta(days=30, minutes=1)
    ).strftime("%b %d %H:%M:%S %Y %Z")

    ssl_environment.ssl_socket.getpeercert.return_value = {
        "notAfter": certificate_expiration,
    }

    result = run_ssl_check(config, TEST_TIMEOUT_SECONDS)

    assert result.success is True
    assert result.message == (
        "SSL certificate for example.com expires in 30 days"
    )
    assert_ssl_dependencies_called(ssl_environment, timeout=TEST_TIMEOUT_SECONDS)


def test_run_ssl_check_returns_failure_for_expired_certificate(
    ssl_environment: SslTestEnvironment,
) -> None:
    config = SslCheckConfig(hostname="example.com")

    certificate_expiration = (
        datetime.now(UTC) - timedelta(days=3) + timedelta(minutes=1)
    ).strftime("%b %d %H:%M:%S %Y %Z")

    ssl_environment.ssl_socket.getpeercert.return_value = {
        "notAfter": certificate_expiration,
    }

    result = run_ssl_check(config, TEST_TIMEOUT_SECONDS)

    assert result.success is False
    assert result.message == (
        "SSL certificate for example.com expired 3 days ago"
    )
    assert_ssl_dependencies_called(ssl_environment, timeout=TEST_TIMEOUT_SECONDS)


def test_run_ssl_check_returns_failure_for_blank_hostname() -> None:
    config = SslCheckConfig(hostname="    ")

    result = run_ssl_check(config, TEST_TIMEOUT_SECONDS)

    assert result.success is False
    assert result.message == "SSL check failed: hostname is empty"


def test_run_ssl_check_returns_failure_for_connection_error() -> None:
    config = SslCheckConfig(hostname="example.com")

    with patch(
        "monitor.checks.socket.create_connection",
        side_effect=OSError("Connection refused"),
    ) as mock_create_connection:
        result = run_ssl_check(config, TEST_TIMEOUT_SECONDS)

    assert result.success is False
    assert result.message == (
        "SSL check failed for example.com: "
        "Connection refused"
    )

    mock_create_connection.assert_called_once_with(
        ("example.com", 443),
        timeout=TEST_TIMEOUT_SECONDS,
    )


def test_run_ssl_check_returns_failure_for_missing_not_after(
    ssl_environment: SslTestEnvironment,
) -> None:
    config = SslCheckConfig(hostname="example.com")

    ssl_environment.ssl_socket.getpeercert.return_value = {}

    result = run_ssl_check(config, TEST_TIMEOUT_SECONDS)

    assert result.success is False
    assert result.message == (
        "SSL certificate for example.com "
        "is missing the expiration date"
    )
    assert_ssl_dependencies_called(ssl_environment, timeout=TEST_TIMEOUT_SECONDS)


def test_run_ssl_check_returns_failure_for_invalid_expiration_date(
    ssl_environment: SslTestEnvironment,
) -> None:
    config = SslCheckConfig(hostname="example.com")

    ssl_environment.ssl_socket.getpeercert.return_value = {
        "notAfter": "invalid date format",
    }

    result = run_ssl_check(config, TEST_TIMEOUT_SECONDS)

    assert result.success is False
    assert result.message == (
        "SSL certificate for example.com "
        "has an invalid expiration date"
    )
    assert_ssl_dependencies_called(ssl_environment, timeout=TEST_TIMEOUT_SECONDS)
