import time
import requests
from monitor.models import HttpCheckResult

def check_http(url: str) -> HttpCheckResult:
    start_time = time.perf_counter()

    try:
        response = requests.get(url, timeout=10)
        end_time = time.perf_counter()
        duration = end_time - start_time

        return HttpCheckResult(
            url=url,
            status_code=response.status_code,
            response_time=duration,
        )

    except requests.RequestException as e:

        end_time = time.perf_counter()
        duration = end_time - start_time
        return HttpCheckResult(
            url=url,
            status_code=None,
            response_time=duration,
            error=str(e),
        )
