import os
import subprocess
import sys
import time
from datetime import UTC, datetime

from croniter import croniter

from monitor.logger import logger

DEFAULT_CRON_SCHEDULE = "*/15 * * * *"


def main() -> None:
    schedule = os.getenv("CRON_SCHEDULE")

    if schedule is None:
        schedule = DEFAULT_CRON_SCHEDULE
        logger.warning(
            "CRON_SCHEDULE is not set. Using default schedule: %s",
            schedule,
        )

    if not croniter.is_valid(schedule):
        raise ValueError(f"Invalid CRON_SCHEDULE: {schedule}")

    logger.info("Scheduler started with schedule: %s", schedule)

    while True:
        now = datetime.now(UTC)
        next_run = croniter(schedule, now).get_next(datetime)
        wait_seconds = (next_run - now).total_seconds()

        logger.info(
            "Next monitoring run at %s UTC",
            next_run.strftime("%Y-%m-%d %H:%M:%S"),
        )

        time.sleep(wait_seconds)

        subprocess.run(
            [sys.executable, "-m", "monitor.main"],
            check=False,
        )


if __name__ == "__main__":
    main()
