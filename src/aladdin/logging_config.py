import logging

LOGGER_NAME = "aladdin"

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Configure centralized logging for Aladdin Analyst AI.

    Parameters
    ----------
    level : int
        Minimum logging level to display.

    Returns
    -------
    logging.Logger
        Configured root logger for the Aladdin package.
    """

    logger = logging.getLogger(LOGGER_NAME)

    logger.setLevel(level)
    logger.propagate = False

    # Prevent duplicate handlers.
    if not logger.handlers:
        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=DATE_FORMAT,
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger within the Aladdin package.

    Parameters
    ----------
    name : str
        Module name for the logger.

    Returns
    -------
    logging.Logger
        A module-specific logger.
    """

    return logging.getLogger(f"{LOGGER_NAME}.{name}")
