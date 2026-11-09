from pathlib import Path
from typing import Any

import pandas as pd

from aladdin.exceptions import UnsupportedFileFormatError
from aladdin.logging_config import get_logger

logger = get_logger("ingestion.json_loader")


def load_json(
    file_path: str | Path,
    **read_json_kwargs: Any,
) -> pd.DataFrame:
    """
    Load a JSON file into a Pandas DataFrame.

    Parameters
    ----------
    file_path : str | Path
        Path to the JSON file.

    **read_json_kwargs : Any
        Additional keyword arguments passed to pandas.read_json().

    Returns
    -------
    pd.DataFrame
        The loaded JSON dataset.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.

    IsADirectoryError
        If the supplied path points to a directory.

    UnsupportedFileFormatError
        If the file does not have a .json extension.
    """

    path = Path(file_path)

    logger.info("Starting JSON ingestion: %s", path.name)

    if not path.exists():
        logger.error("JSON file not found: %s", path.name)
        raise FileNotFoundError(f"JSON file not found: {path}")

    if not path.is_file():
        logger.error("Expected a JSON file, received a directory: %s", path.name)
        raise IsADirectoryError(
            f"Expected a JSON file, but received a directory: {path}"
        )

    if path.suffix.lower() != ".json":
        logger.error(
            "Unsupported JSON file extension: %s",
            path.suffix or "no extension",
        )
        raise UnsupportedFileFormatError(
            f"Expected a .json file, received: {path.suffix or 'no extension'}"
        )

    logger.debug("JSON file validation completed: %s", path.name)

    try:
        dataframe = pd.read_json(path, **read_json_kwargs)

    except Exception:
        logger.exception("Failed to load JSON file: %s", path.name)
        raise

    logger.info(
        "Successfully loaded JSON: %s | rows=%d | columns=%d",
        path.name,
        len(dataframe),
        len(dataframe.columns),
    )

    return dataframe
