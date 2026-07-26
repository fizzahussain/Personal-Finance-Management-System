import logging
import os
from logging.config import dictConfig
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT_LOG_LEVELS = {
    "development": "DEBUG",
    "testing": "WARNING",
    "production": "INFO",
}

VALID_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


def get_environment() -> str:
    """Return the current application environment"""
    return os.getenv(
        "APP_ENV",
        "development",
    ).strip().lower()


def get_log_level() -> str:
    """Return the configured logging level"""
    configured_level = os.getenv("LOG_LEVEL")

    if configured_level:
        normalized_level = (
            configured_level.strip().upper()
        )

        if normalized_level in VALID_LOG_LEVELS:
            return normalized_level

    environment = get_environment()

    return ENVIRONMENT_LOG_LEVELS.get(
        environment,
        "INFO",
    )


def configure_logging() -> None:
    """Configure console and rotating file logs"""
    log_directory = Path("logs")

    log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_level = get_log_level()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": (
                        "%(asctime)s | "
                        "%(levelname)s | "
                        "%(name)s | "
                        "%(message)s"
                    ),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": log_level,
                    "formatter": "standard",
                },
                "application_file": {
                    "class": (
                        "logging.handlers."
                        "RotatingFileHandler"
                    ),
                    "level": log_level,
                    "formatter": "standard",
                    "filename": (
                        "logs/personal-finance.log"
                    ),
                    "maxBytes": 1_000_000,
                    "backupCount": 3,
                    "encoding": "utf-8",
                },
                "error_file": {
                    "class": (
                        "logging.handlers."
                        "RotatingFileHandler"
                    ),
                    "level": "ERROR",
                    "formatter": "standard",
                    "filename": (
                        "logs/personal-finance-error.log"
                    ),
                    "maxBytes": 1_000_000,
                    "backupCount": 3,
                    "encoding": "utf-8",
                },
            },
            "root": {
                "level": log_level,
                "handlers": [
                    "console",
                    "application_file",
                    "error_file",
                ],
            },
            "loggers": {
                "uvicorn": {
                    "level": log_level,
                    "handlers": [
                        "console",
                        "application_file",
                        "error_file",
                    ],
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": log_level,
                    "handlers": [
                        "console",
                        "application_file",
                        "error_file",
                    ],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": "INFO",
                    "handlers": [
                        "console",
                        "application_file",
                    ],
                    "propagate": False,
                },
            },
        }
    )

    logger = logging.getLogger(__name__)

    logger.info(
        "Logging configured environment=%s level=%s",
        get_environment(),
        log_level,
    )

    logger.debug(
        "Debug logging is enabled"
    )


def get_logger(
    name: str,
) -> logging.Logger:
    """Return a named logger"""
    return logging.getLogger(name)