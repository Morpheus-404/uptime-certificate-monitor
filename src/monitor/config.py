from dataclasses import dataclass
from pathlib import Path

import yaml

@dataclass
class HttpCheckConfig:
    url: str

@dataclass
class SslCheckConfig:
    hostname: str


@dataclass
class Config:
    checks: list[HttpCheckConfig | SslCheckConfig]
    request_timeout_seconds: float = 10.0

def load_config(path: Path) -> Config:
    with path.open() as file:
        data = yaml.safe_load(file)

    request_timeout_seconds = float(
        data.get("request_timeout_seconds", 10.0)
    )
    if request_timeout_seconds <= 0:
        raise ValueError("request_timeout_seconds must be greater than 0")

    checks = []

    for check in data["checks"]:
        if check["type"] == "http":
            checks.append(HttpCheckConfig(url=check["url"]))

        elif check["type"] == "ssl":
            checks.append(SslCheckConfig(hostname=check["hostname"]))

        else:
            raise ValueError(f"Unknown check type: {check['type']}")
    return Config(
        checks=checks,
        request_timeout_seconds=request_timeout_seconds,
    )
