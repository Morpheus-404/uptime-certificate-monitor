import ssl
from datetime import date
from unittest.mock import patch

from monitor.ssl_check import check_ssl


@patch("monitor.ssl_check.socket.create_connection")
@patch("monitor.ssl_check.ssl.create_default_context")
def test_check_ssl_returns_certificate_data(
    mock_create_default_context,
    mock_create_connection,
):
    # Arrange
    certificate = {
        "notAfter": "Aug 29 21:41:26 2026 GMT",
        "issuer": ((("commonName", "Test Issuer"),),),
        "subject": ((("commonName", "example.com"),),),
    }
    mock_sock = (
        mock_create_connection.return_value.__enter__.return_value
    )
    mock_context = mock_create_default_context.return_value
    mock_ssock = (
        mock_context.wrap_socket.return_value.__enter__.return_value
    )
    mock_ssock.getpeercert.return_value = certificate

    # Act
    result = check_ssl("example.com")

    # Assert
    assert result.url == "example.com"
    assert result.expiration_date == date(2026, 8, 29)
    assert result.issuer == "Test Issuer"
    assert result.subject == "example.com"
    assert result.error is None
    mock_context.wrap_socket.assert_called_once_with(
        mock_sock,
        server_hostname="example.com",
    )
    mock_create_connection.assert_called_once_with(
        ("example.com", 443),
        timeout=10,
    )
    mock_create_default_context.assert_called_once_with()
    mock_ssock.getpeercert.assert_called_once_with()


@patch("monitor.ssl_check.socket.create_connection")
@patch("monitor.ssl_check.ssl.create_default_context")
def test_check_ssl_returns_error_if_not_after_has_wrong_format(
    mock_create_default_context,
    _mock_create_connection,
):
    # Arrange
    certificate = {
        "notAfter": "no Date",
        "issuer": ((("commonName", "Test Issuer"),),),
        "subject": ((("commonName", "example.com"),),),
    }
    mock_context = mock_create_default_context.return_value
    mock_ssock = (
        mock_context.wrap_socket.return_value.__enter__.return_value
    )
    mock_ssock.getpeercert.return_value = certificate

    # Act
    result = check_ssl("example.com")

    # Assert
    assert result.url == "example.com"
    assert "no Date" in result.error


@patch("monitor.ssl_check.socket.create_connection")
@patch("monitor.ssl_check.ssl.create_default_context")
def test_check_ssl_returns_error_if_not_after_is_missing(
    mock_create_default_context,
    _mock_create_connection,
):
    # Arrange
    certificate = {
        "EndDate": "Aug 29 21:41:26 2026 GMT",
        "issuer": ((("commonName", "Test Issuer"),),),
        "subject": ((("commonName", "example.com"),),),
    }
    mock_context = mock_create_default_context.return_value
    mock_ssock = (
        mock_context.wrap_socket.return_value.__enter__.return_value
    )
    mock_ssock.getpeercert.return_value = certificate

    # Act
    result = check_ssl("example.com")

    # Assert
    assert result.url == "example.com"
    assert "notAfter" in result.error


@patch("monitor.ssl_check.socket.create_connection")
def test_check_ssl_returns_error_if_connection_fails(
    mock_create_connection,
):
    # Arrange
    mock_create_connection.side_effect = OSError("Connection failed")

    # Act
    result = check_ssl("example.com")

    # Assert
    assert result.url == "example.com"
    assert result.error == "Connection failed"


@patch("monitor.ssl_check.socket.create_connection")
@patch("monitor.ssl_check.ssl.create_default_context")
def test_check_ssl_returns_error_if_ssl_connection_fails(
    mock_create_default_context,
    _mock_create_connection,
):
    # Arrange
    mock_context = mock_create_default_context.return_value
    mock_context.wrap_socket.side_effect = ssl.SSLError(
        "SSL handshake failed"
    )

    # Act
    result = check_ssl("example.com")

    # Assert
    assert result.url == "example.com"
    assert "SSL handshake failed" in result.error

