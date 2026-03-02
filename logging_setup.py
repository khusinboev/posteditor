import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(level: int = logging.INFO, log_file: str = "logs/app.log") -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
