import os
from pathlib import Path

from monitor.config import load_config
from monitor.logger import logger
from monitor.monitor import run_checks
from monitor.notifier import (
    build_failure_message,
    send_discord_notification,
)


def main() -> int:
    config = load_config(Path("config.yaml"))
    results = run_checks(config)

    for result in results:
        if result.success:
            logger.info(result.message)
        else:
            logger.error(result.message)

    failed_results = [
        result
        for result in results
        if not result.success
    ]

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if failed_results and webhook_url:
        message = build_failure_message(failed_results)

        send_discord_notification(
            webhook_url,
            message,
        )

    if failed_results:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
