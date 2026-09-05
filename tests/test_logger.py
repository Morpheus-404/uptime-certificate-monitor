import logging
import time

from monitor.logger import LOG_FILE, logger


def test_logger_has_console_and_file_handler() -> None:
    handlers = logger.handlers

    assert any(
        type(handler) is logging.StreamHandler
        for handler in handlers
    )

    assert any(
        isinstance(handler, logging.FileHandler)
        for handler in handlers
    )


def test_logger_uses_utc() -> None:
    for handler in logger.handlers:
        assert handler.formatter is not None
        assert handler.formatter.converter is time.gmtime


def test_logger_writes_to_monitor_log() -> None:
    file_handlers = [
        handler
        for handler in logger.handlers
        if isinstance(handler, logging.FileHandler)
    ]

    assert len(file_handlers) == 1
    assert file_handlers[0].baseFilename.endswith(str(LOG_FILE))
