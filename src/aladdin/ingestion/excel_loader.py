from pathlib import Path
from typing import Any

import pandas as pd

from aladdin.exceptions import UnsupportedFileFormatError
from aladdin.logging_config import get_logger

logger = get_logger("ingestion.excel_loader")


def load_excel(
    file_path: str | Path,
    **read_excel_kwargs: Any,
) -> pd.DataFrame:
    """
    Load an Excel worksheet into a Pandas DataFrame.

    Parameters
    ----------
    file_path : str | Path
        Path to the Excel file.

    **read_excel_kwargs : Any
        Additional keyword arguments passed to pandas.read_excel().

    Returns
    -------
    pd.DataFrame
        The loaded worksheet.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.

    IsADirectoryError
        If the supplied path points to a directory.

    UnsupportedFileFormatError
        If the file does not have an .xlsx extension.
    """

    path = Path(file_path)

    logger.info("Starting Excel ingestion: %s", path.name)

    if not path.exists():
        logger.error("Excel file not found: %s", path.name)
        raise FileNotFoundError(f"Excel file not found: {path}")

    if not path.is_file():
        logger.error("Expected an Excel file, received a directory: %s", path.name)
        raise IsADirectoryError(
            f"Expected an Excel file, but received a directory: {path}"
        )

    if path.suffix.lower() != ".xlsx":
        logger.error(
            "Unsupported Excel file extension: %s",
            path.suffix or "no extension",
        )
        raise UnsupportedFileFormatError(
            f"Expected an .xlsx file, received: {path.suffix or 'no extension'}"
        )

    logger.debug("Excel file validation completed: %s", path.name)

    try:
        dataframe = pd.read_excel(
            path,
            engine="openpyxl",
            **read_excel_kwargs,
        )

    except Exception:
        logger.exception("Failed to load Excel file: %s", path.name)
        raise

    logger.info(
        "Successfully loaded Excel: %s | rows=%d | columns=%d",
        path.name,
        len(dataframe),
        len(dataframe.columns),
    )

    return dataframe
