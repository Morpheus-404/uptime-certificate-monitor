import pytest
from pathlib import Path
from monitor.config import HttpCheckConfig, SslCheckConfig, load_config


def test_load_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"

    config_file.write_text(
        """
checks:
  - type: http
    url: https://example.com

  - type: ssl
    hostname: example.com
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

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
