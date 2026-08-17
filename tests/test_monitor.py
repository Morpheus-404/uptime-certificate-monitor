from unittest.mock import patch

import pytest

from monitor.checks import CheckResult
from monitor.config import Config, HttpCheckConfig, SslCheckConfig
from monitor.monitor import run_checks


def test_run_checks_runs_ssl_check() -> None:
    config = Config(
        checks=[
            SslCheckConfig(hostname="example.com"),
        ],
        request_timeout_seconds=8.5,
    )

    with patch(
        "monitor.monitor.run_ssl_check",
        return_value=CheckResult(
            success=True,
            message="SSL check for example.com: OK"
            ),
    ) as mock_run_ssl_check:

        results = run_checks(config)

    mock_run_ssl_check.assert_called_once_with(
        config.checks[0],
        config.request_timeout_seconds,
    )
    assert results == [
        CheckResult(
            success=True,
            message="SSL check for example.com: OK"
        )
    ]


def test_run_checks_runs_http_check() -> None:
    config = Config(
        checks=[
            HttpCheckConfig(url="https://example.com"),
        ],
        request_timeout_seconds=8.5,
    )

    with patch(
        "monitor.monitor.run_http_check",
        return_value=CheckResult(
            success=True,
            message="HTTP check for https://example.com: OK"
        ),
    ) as mock_run_http_check:
        results = run_checks(config)

    mock_run_http_check.assert_called_once_with(
        config.checks[0],
        config.request_timeout_seconds,
    )
    assert results == [
        CheckResult(
            success=True,
            message="HTTP check for https://example.com: OK"
        )
    ]


def test_run_checks_runs_multiple_checks() -> None:
    config = Config(
        checks=[
            HttpCheckConfig(url="https://example.com"),
            SslCheckConfig(hostname="example.com"),
        ],
        request_timeout_seconds=8.5,
    )

    http_check_result = CheckResult(
        success=True,
        message="HTTP check for https://example.com: OK"
    )

    ssl_check_result = CheckResult(
        success=True,
        message="SSL check for example.com: OK"
    )

    with (
        patch(
            "monitor.monitor.run_http_check",
            return_value=http_check_result,
        ) as mock_run_http_check,
        patch(
            "monitor.monitor.run_ssl_check",
            return_value=ssl_check_result,
        ) as mock_run_ssl_check,
    ):
        results = run_checks(config)

    mock_run_http_check.assert_called_once_with(
        config.checks[0],
        config.request_timeout_seconds,
    )
    mock_run_ssl_check.assert_called_once_with(
        config.checks[1],
        config.request_timeout_seconds,
    )

    assert results == [
        http_check_result,
        ssl_check_result,
    ]


def test_run_checks_raises_type_error_for_unsupported_check() -> None:
    config = Config(
        checks=[object()]
    )

    with pytest.raises(
        TypeError,
        match="Unsupported check configuration: object",
    ):

        run_checks(config)
