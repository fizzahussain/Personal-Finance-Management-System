import logging
from pathlib import Path

LOGGER_NAME = "personal_finance_analytics_system"


def configure_logging(
    file_path: str = "logs/app.log",
) -> logging.Logger:
    """Configure and return the application logger"""
    path = Path(file_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in logger.handlers:
        handler.close()

    logger.handlers.clear()

    file_handler = logging.FileHandler(
        path,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s"
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    """Return the application logger"""
    return logging.getLogger(LOGGER_NAME)