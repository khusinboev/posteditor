import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(level: int = logging.INFO, log_file: str = "logs/app.log") -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    base_dir = Path(__file__).resolve().parent
    resolved_log_file = Path(log_file)
    if not resolved_log_file.is_absolute():
        resolved_log_file = (base_dir / resolved_log_file).resolve()

    os.makedirs(resolved_log_file.parent, exist_ok=True)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    file_handler = RotatingFileHandler(str(resolved_log_file), maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
