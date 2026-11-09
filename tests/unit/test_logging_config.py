import logging
from io import StringIO

from aladdin.logging_config import (
    DATE_FORMAT,
    LOG_FORMAT,
    configure_logging,
    get_logger,
)


def test_configure_logging_returns_aladdin_logger():
    """Test centralized logger configuration."""

    logger = configure_logging()

    assert isinstance(logger, logging.Logger)
    assert logger.name == "aladdin"


def test_configure_logging_does_not_add_duplicate_handlers():
    """Test that repeated configuration avoids duplicate handlers."""

    logger = configure_logging()

    initial_handler_count = len(logger.handlers)

    configure_logging()

    assert len(logger.handlers) == initial_handler_count


def test_get_logger_returns_module_specific_logger():
    """Test creation of module-specific loggers."""

    logger = get_logger("ingestion.csv_loader")

    assert logger.name == "aladdin.ingestion.csv_loader"


def test_logger_writes_messages_to_console():
    """Test that a logger writes correctly formatted console output."""

    configure_logging(level=logging.INFO)

    logger = get_logger("test_module")

    # Use an independent stream instead of pytest's temporary stderr.
    output_stream = StringIO()

    handler = logging.StreamHandler(output_stream)

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    handler.setFormatter(formatter)

    # Isolate this test from the existing logging handlers.
    logger.addHandler(handler)
    logger.propagate = False

    try:
        logger.info("Test logging message")

        output = output_stream.getvalue()

        assert "INFO" in output
        assert "aladdin.test_module" in output
        assert "Test logging message" in output

    finally:
        logger.removeHandler(handler)
        logger.propagate = True
        handler.close()
