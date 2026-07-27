import urllib.request
import socket
import ssl
from dataclasses import dataclass
from datetime import datetime, UTC

from monitor.config import HttpCheckConfig, SslCheckConfig


@dataclass
class CheckResult:
    success: bool
    message: str


def run_http_check(config: HttpCheckConfig) -> CheckResult:
    with urllib.request.urlopen(config.url) as response:
        status = response.status

        return CheckResult(
            success=status == 200,
            message=f"HTTP status: {status}",
        )


def run_ssl_check(config: SslCheckConfig) -> CheckResult:
    context = ssl.create_default_context()

    with socket.create_connection((config.hostname, 443)) as connection:
        with context.wrap_socket(
            connection,
            server_hostname=config.hostname,
        ) as secure_connection:
            certificate = secure_connection.getpeercert()

    expires_at = datetime.strptime(
        certificate["notAfter"],
        "%b %d %H:%M:%S %Y %Z",
    ).replace(tzinfo=UTC)

    days_remaining = (expires_at - datetime.now(UTC)).days

    return CheckResult(
        success=days_remaining > 0,
        message=(
            f"SSL certificate for {config.hostname} "
            f"expires in {days_remaining} days"
        ),
    )
