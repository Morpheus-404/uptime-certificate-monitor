import urllib.request
import socket
import ssl
from dataclasses import dataclass
from datetime import datetime, UTC
from urllib.error import URLError, HTTPError

from monitor.config import HttpCheckConfig, SslCheckConfig


CHECK_TIMEOUT_SECONDS = 10


@dataclass
class CheckResult:
    success: bool
    message: str


def run_http_check(config: HttpCheckConfig) -> CheckResult:
    url = config.url.strip()

    if not url:
        return CheckResult(
            success=False,
            message="HTTP check failed: URL is empty",
        )

    try:
        with urllib.request.urlopen(
            url,
            timeout=CHECK_TIMEOUT_SECONDS,
        ) as response:
            status = response.status

            return CheckResult(
                success=status == 200,
                message=(
                    f"HTTP status for {url}: {status}"
                )
            )

    except HTTPError as error:
        return CheckResult(
            success=False,
            message=(
                f"HTTP check failed for {url}: "
                f"status {error.code}: {error.reason}"
            ),
        )

    except URLError as error:
        return CheckResult(
            success=False,
            message=(
                f"HTTP check failed for {url}: "
                f"{error.reason}"
            ),
        )


def run_ssl_check(config: SslCheckConfig) -> CheckResult:
    hostname = config.hostname.strip()

    if not hostname:
        return CheckResult(
            success=False,
            message="SSL check failed: hostname is empty",
        )

    try:
        context = ssl.create_default_context()

        with socket.create_connection(
            (hostname, 443),
            timeout=CHECK_TIMEOUT_SECONDS,
        ) as connection:
            with context.wrap_socket(
                connection,
                server_hostname=hostname,
            ) as secure_connection:
                certificate = secure_connection.getpeercert()

        not_after = certificate["notAfter"]
        now = datetime.now(UTC)

        expires_at = datetime.strptime(
            not_after,
            "%b %d %H:%M:%S %Y %Z",
        ).replace(tzinfo=UTC)

        days_remaining = (expires_at - now).days

        if expires_at <= now:
            return CheckResult(
                success=False,
                message=(
                    f"SSL certificate for {hostname} "
                    f"expired {-days_remaining} days ago"
                ),
            )

        return CheckResult(
            success=True,
            message=(
                f"SSL certificate for {hostname} "
                f"expires in {days_remaining} days"
            ),
        )

    except OSError as error:
        return CheckResult(
            success=False,
            message=(
                f"SSL check failed for {hostname}: "
                f"{error}"
            ),
        )

    except KeyError:
        return CheckResult(
            success=False,
            message=(
                f"SSL certificate for {hostname} "
                "is missing the expiration date"
            ),
        )

    except ValueError:
        return CheckResult(
            success=False,
            message=(
                f"SSL certificate for {hostname} "
                "has an invalid expiration date"
            ),
        )
