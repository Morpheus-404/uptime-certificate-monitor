from pathlib import Path

import pytest

from monitor.config import HttpCheckConfig, SslCheckConfig, load_config


def test_load_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"

    config_file.write_text(
          """
request_timeout_seconds: 10.0
checks:
  - type: http
    url: https://example.com

  - type: ssl
    hostname: example.com
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.request_timeout_seconds == 10.0
    assert config.checks == [
        HttpCheckConfig(url="https://example.com"),
        SslCheckConfig(hostname="example.com"),
    ]

def test_load_config_rejects_unknown_check_type(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"

    config_file.write_text(
          """
checks:
  - type: ftp
    hostname: https://example.com
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown check type: ftp"):
      load_config(config_file)

def test_load_config_reads_request_timeout_seconds(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
          """
request_timeout_seconds: 8.5
checks:
  - type: http
    url: https://example.com

  - type: ssl
    hostname: example.com
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.request_timeout_seconds == 8.5


@pytest.mark.parametrize("timeout", [0.0, -1.0])
def test_load_config_rejects_non_positive_request_timeout_seconds(
    tmp_path: Path,
    timeout: float,
) -> None:
    config_file = tmp_path / "config.yaml"

    config_file.write_text(
        f"""
request_timeout_seconds: {timeout}
checks:
  - type: http
    url: https://example.com

  - type: ssl
    hostname: example.com
""",
        encoding="utf-8",
    )

    with pytest.raises(
      ValueError,
      match="request_timeout_seconds must be greater than 0",
    ):
        load_config(config_file)
