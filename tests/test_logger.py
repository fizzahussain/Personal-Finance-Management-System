from personal_finance_analytics_system.logger import (
    configure_logging,
)


def test_logger_creates_log_file(tmp_path) -> None:
    """Create the log file"""
    file_path = tmp_path / "logs" / "app.log"

    logger = configure_logging(str(file_path))
    logger.info("Application started")

    for handler in logger.handlers:
        handler.flush()

    assert file_path.exists()


def test_logger_writes_message(tmp_path) -> None:
    """Write a message to the log file"""
    file_path = tmp_path / "app.log"

    logger = configure_logging(str(file_path))
    logger.info("Transaction added")

    for handler in logger.handlers:
        handler.flush()

    content = file_path.read_text(
        encoding="utf-8",
    )

    assert "INFO" in content
    assert "Transaction added" in content