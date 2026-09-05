import logging
import time
from pathlib import Path

LOG_DIRECTORY = Path("logs")
LOG_FILE = LOG_DIRECTORY / "monitor.log"
LOG_FORMAT = "%(asctime)s UTC - %(levelname)s - %(message)s"

LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

formatter = logging.Formatter(LOG_FORMAT)
formatter.converter = time.gmtime

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)

logger = logging.getLogger("monitor")
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
