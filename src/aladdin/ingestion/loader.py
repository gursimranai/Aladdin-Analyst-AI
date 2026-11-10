from collections.abc import Callable
from pathlib import Path
from typing import Any

import pandas as pd

from aladdin.exceptions import UnsupportedFileFormatError
from aladdin.ingestion.csv_loader import load_csv
from aladdin.ingestion.excel_loader import load_excel
from aladdin.ingestion.json_loader import load_json
from aladdin.ingestion.parquet_loader import load_parquet

LoaderFunction = Callable[..., pd.DataFrame]


_LOADERS: dict[str, LoaderFunction] = {
    ".csv": load_csv,
    ".xlsx": load_excel,
    ".json": load_json,
    ".parquet": load_parquet,
}


def load_data(
    file_path: str | Path,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Automatically load a supported data file.

    The loader is selected based on the file extension.

    Parameters
    ----------
    file_path : str | Path
        Path to the data file.

    **kwargs : Any
        Additional keyword arguments passed to the selected loader.

    Returns
    -------
    pd.DataFrame
        The loaded dataset.

    Raises
    ------
    UnsupportedFileFormatError
        If the file extension is not supported.
    """

    path = Path(file_path)

    loader = _LOADERS.get(path.suffix.lower())

    if loader is None:
        supported_formats = ", ".join(_LOADERS)

        raise UnsupportedFileFormatError(
            f"Unsupported file format: {path.suffix or 'no extension'}. "
            f"Supported formats: {supported_formats}"
        )

    return loader(path, **kwargs)
