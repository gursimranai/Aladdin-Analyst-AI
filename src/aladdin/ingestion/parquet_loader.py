from pathlib import Path
from typing import Any

import pandas as pd

from aladdin.exceptions import UnsupportedFileFormatError
from aladdin.logging_config import get_logger

logger = get_logger("ingestion.parquet_loader")


def load_parquet(
    file_path: str | Path,
    **read_parquet_kwargs: Any,
) -> pd.DataFrame:
    """
    Load a Parquet file into a Pandas DataFrame.

    Parameters
    ----------
    file_path : str | Path
        Path to the Parquet file.

    **read_parquet_kwargs : Any
        Additional keyword arguments passed to pandas.read_parquet().

    Returns
    -------
    pd.DataFrame
        The loaded Parquet dataset.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.

    IsADirectoryError
        If the supplied path points to a directory.

    UnsupportedFileFormatError
        If the file does not have a .parquet extension.
    """

    path = Path(file_path)

    logger.info("Starting Parquet ingestion: %s", path.name)

    if not path.exists():
        logger.error("Parquet file not found: %s", path.name)
        raise FileNotFoundError(f"Parquet file not found: {path}")

    if not path.is_file():
        logger.error(
            "Expected a Parquet file, received a directory: %s",
            path.name,
        )
        raise IsADirectoryError(
            f"Expected a Parquet file, but received a directory: {path}"
        )

    if path.suffix.lower() != ".parquet":
        logger.error(
            "Unsupported Parquet file extension: %s",
            path.suffix or "no extension",
        )
        raise UnsupportedFileFormatError(
            f"Expected a .parquet file, received: {path.suffix or 'no extension'}"
        )

    logger.debug("Parquet file validation completed: %s", path.name)

    try:
        dataframe = pd.read_parquet(
            path,
            engine="pyarrow",
            **read_parquet_kwargs,
        )

    except Exception:
        logger.exception("Failed to load Parquet file: %s", path.name)
        raise

    logger.info(
        "Successfully loaded Parquet: %s | rows=%d | columns=%d",
        path.name,
        len(dataframe),
        len(dataframe.columns),
    )

    return dataframe
