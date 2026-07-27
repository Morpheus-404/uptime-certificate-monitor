from pathlib import Path

from monitor.checks import run_http_check, run_ssl_check
from monitor.config import HttpCheckConfig, SslCheckConfig, load_config


def main() -> None:
    config = load_config(Path("config.yaml"))

    for check in config.checks:

        if isinstance(check, HttpCheckConfig):
            result = run_http_check(check)
            print(result)

        elif isinstance(check, SslCheckConfig):
            result = run_ssl_check(check)
            print(result)


if __name__ == "__main__":
    main()
