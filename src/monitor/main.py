from pathlib import Path

from monitor.config import load_config
from monitor.monitor import run_checks


def main() -> int:
    config = load_config(Path("config.yaml"))

    results = run_checks(config)

    for result in results:
        print(result.message)

    if any(not result.success for result in results):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
