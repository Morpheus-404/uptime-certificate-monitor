from unittest.mock import patch, Mock
from monitor.http_check import check_http
import requests
import pytest


def test_check_http_returns_status_code():
    mock_response = Mock(status_code=200)

    with patch("monitor.http_check.requests.get") as mock_get:
        mock_get.return_value = mock_response

        result = check_http("https://www.example.com")

        assert result.status_code == 200


def test_check_http_calls_requests_get_with_url_and_timeout():

    with patch("monitor.http_check.requests.get") as mock_get:

        check_http("https://www.example.com")

        mock_get.assert_called_once_with(
            "https://www.example.com",
            timeout=10
        )


def test_check_http_returns_error_if_request_fails():

    with patch("monitor.http_check.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Test error")

        result = check_http("https://www.example.com")
        assert result.error == "Test error"


def test_check_http_returns_none_status_code_if_request_fails():

    with patch("monitor.http_check.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Test error")
        result = check_http("https://www.example.com")
        assert result.status_code is None


def test_check_http_returns_correct_response_time():

    mock_response = Mock(status_code=200)

    with (
        patch("monitor.http_check.requests.get") as mock_get,
        patch("monitor.http_check.time.perf_counter") as mock_perf_counter
    ):
        mock_get.return_value = mock_response
        mock_perf_counter.side_effect = [1.0, 2.0]

        result = check_http("https://www.example.com")

        assert result.response_time == pytest.approx(1.0)
