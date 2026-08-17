from dataclasses import dataclass
from datetime import date


@dataclass
class HttpCheckResult:
    url: str
    status_code: int | None
    response_time: float
    error: str | None = None

@dataclass
class SslCheckResult:
    url: str
    expiration_date: date | None = None
    issuer: str | None = None
    subject: str | None = None
    error: str | None = None
    