from monitor.checks import run_http_check, run_ssl_check, CheckResult
from monitor.config import Config, HttpCheckConfig, SslCheckConfig



def run_checks(config: Config) -> list[CheckResult]:
    results: list[CheckResult] = []

    for check in config.checks:
        if isinstance(check, HttpCheckConfig):
            result = run_http_check(check)
        elif isinstance(check, SslCheckConfig):
            result = run_ssl_check(check)

        else:
            raise TypeError(
                f"Unsupported check configuration: {type(check).__name__}"
            )

        results.append(result)

    return results
