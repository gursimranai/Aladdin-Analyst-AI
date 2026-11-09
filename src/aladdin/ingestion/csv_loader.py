from pathlib import Path
from typing import Any

import pandas as pd

from aladdin.exceptions import UnsupportedFileFormatError
from aladdin.logging_config import get_logger

logger = get_logger("ingestion.csv_loader")


def load_csv(
    file_path: str | Path,
    **read_csv_kwargs: Any,
) -> pd.DataFrame:
    """
    Load a CSV file into a Pandas DataFrame.

    Parameters
    ----------
    file_path : str | Path
        Path to the CSV file.

    **read_csv_kwargs : Any
        Additional keyword arguments passed to pandas.read_csv().

    Returns
    -------
    pd.DataFrame
        The loaded dataset.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.

    IsADirectoryError
        If the supplied path points to a directory.

    UnsupportedFileFormatError
        If the file does not have a .csv extension.
    """

    path = Path(file_path)

    logger.info("Starting CSV ingestion: %s", path.name)

    if not path.exists():
        logger.error("CSV file not found: %s", path.name)
        raise FileNotFoundError(f"CSV file not found: {path}")

    if not path.is_file():
        logger.error("Expected a CSV file, received a directory: %s", path.name)
        raise IsADirectoryError(
            f"Expected a CSV file, but received a directory: {path}"
        )

    if path.suffix.lower() != ".csv":
        logger.error(
            "Unsupported file extension: %s",
            path.suffix or "no extension",
        )
        raise UnsupportedFileFormatError(
            f"Expected a .csv file, received: {path.suffix or 'no extension'}"
        )

    logger.debug("CSV file validation completed: %s", path.name)

    try:
        dataframe = pd.read_csv(path, **read_csv_kwargs)

    except Exception:
        logger.exception("Failed to load CSV file: %s", path.name)
        raise

    logger.info(
        "Successfully loaded CSV: %s | rows=%d | columns=%d",
        path.name,
        len(dataframe),
        len(dataframe.columns),
    )

    return dataframe
