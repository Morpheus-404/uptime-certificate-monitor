import ssl
import socket
from datetime import datetime

from monitor.models import SslCheckResult


def get_common_name(name_data) -> str | None:
    for name in name_data:
        if name[0][0] == "commonName":
            return name[0][1]
    return None


def check_ssl(hostname: str) -> SslCheckResult:
    try:
        context = ssl.create_default_context()
        with (
            socket.create_connection((hostname, 443), timeout=10) as sock,
            context.wrap_socket(sock, server_hostname=hostname) as ssock,
        ):
            cert = ssock.getpeercert()

            return SslCheckResult(
                url=hostname,
                expiration_date=datetime.strptime(
                    cert["notAfter"],
                    "%b %d %H:%M:%S %Y %Z",
                ).date(),
                issuer=get_common_name(cert["issuer"]),
                subject=get_common_name(cert["subject"]),
            )

    except (OSError, ssl.SSLError, ValueError, KeyError) as e:
        return SslCheckResult(
            url=hostname,
            error=str(e),
        )
