import json
import urllib.request
from urllib.error import HTTPError, URLError

from monitor.checks import CHECK_TIMEOUT_SECONDS, CheckResult
from monitor.logger import logger



def build_failure_message(
    failed_results: list[CheckResult],
) -> str:
    messages = [
        f"- {result.message}"
        for result in failed_results
    ]

    return "Monitoring checks failed:\n" + "\n".join(messages)


def send_discord_notification(
    webhook_url: str,
    message: str,
) -> None:
    payload = {
        "content": message,
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        webhook_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "uptime-certificate-monitor/0.1",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=CHECK_TIMEOUT_SECONDS,
        ):
            pass

    except HTTPError as error:
        logger.error(
            "Discord notification failed with HTTP status %s: %s",
            error.code,
            error.reason,
        )

    except URLError as error:
        logger.error(
            "Discord notification failed: %s",
            error.reason,
        )
