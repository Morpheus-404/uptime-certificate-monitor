import yaml
from dataclasses import dataclass
from pathlib import Path

@dataclass
class HttpCheckConfig:
    url: str

@dataclass
class SslCheckConfig:
    hostname: str


@dataclass
class Config:
    checks: list[HttpCheckConfig | SslCheckConfig]

def load_config(path: Path) -> Config:
    with path.open() as file:
        data = yaml.safe_load(file)

    checks = []

    for check in data["checks"]:
        if check["type"] == "http":
            checks.append(HttpCheckConfig(url=check["url"]))

        elif check["type"] == "ssl":
            checks.append(SslCheckConfig(hostname=check["hostname"]))

        else:
            raise ValueError(f"Unknown check type: {check['type']}")
    return Config(checks=checks)
