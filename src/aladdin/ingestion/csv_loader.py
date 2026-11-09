from pathlib import Path
from typing import Any

import pandas as pd

from aladdin.exceptions import UnsupportedFileFormatError


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

    ValueError
        If the file does not have a .csv extension.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    if not path.is_file():
        raise IsADirectoryError(
            f"Expected a CSV file, but received a directory: {path}"
        )

    if path.suffix.lower() != ".csv":
        raise UnsupportedFileFormatError(
            f"Expected a .csv file, received: {path.suffix or 'no extension'}"
        )

    return pd.read_csv(path, **read_csv_kwargs)
