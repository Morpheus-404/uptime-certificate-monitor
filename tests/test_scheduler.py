from unittest.mock import Mock

import pytest

from monitor import scheduler


def test_invalid_cron_schedule_raises_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CRON_SCHEDULE", "invalid")

    with pytest.raises(ValueError, match="Invalid CRON_SCHEDULE"):
        scheduler.main()


def test_scheduler_uses_default_schedule_when_env_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CRON_SCHEDULE", raising=False)

    mock_logger = Mock()
    monkeypatch.setattr(scheduler, "logger", mock_logger)

    def stop_scheduler(_: float) -> None:
        raise RuntimeError("stop")

    monkeypatch.setattr(scheduler.time, "sleep", stop_scheduler)

    with pytest.raises(RuntimeError, match="stop"):
        scheduler.main()

    mock_logger.warning.assert_called_once_with(
        "CRON_SCHEDULE is not set. Using default schedule: %s",
        scheduler.DEFAULT_CRON_SCHEDULE,
    )

    mock_logger.info.assert_any_call(
        "Scheduler started with schedule: %s",
        scheduler.DEFAULT_CRON_SCHEDULE,
    )


def test_scheduler_runs_monitor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CRON_SCHEDULE", "* * * * *")

    mock_logger = Mock()
    monkeypatch.setattr(scheduler, "logger", mock_logger)
    monkeypatch.setattr(scheduler.time, "sleep", lambda _: None)

    mock_run = Mock(side_effect=RuntimeError("stop"))
    monkeypatch.setattr(scheduler.subprocess, "run", mock_run)

    with pytest.raises(RuntimeError, match="stop"):
        scheduler.main()

    mock_run.assert_called_once_with(
        [
            scheduler.sys.executable,
            "-m",
            "monitor.main",
        ],
        check=False,
    )
