import pandas as pd
import pyarrow
import pytest
from pandas.testing import assert_frame_equal

from aladdin.exceptions import UnsupportedFileFormatError
from aladdin.ingestion.parquet_loader import load_parquet


@pytest.fixture
def sample_parquet_file(tmp_path):
    """Create a temporary Parquet file for testing."""

    dataframe = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "price": [75000, 1200, 2500],
            "quantity": [2, 10, 5],
        }
    )

    file_path = tmp_path / "sales.parquet"

    dataframe.to_parquet(
        file_path,
        engine="pyarrow",
        index=False,
    )

    return file_path, dataframe


def test_load_parquet_successfully(sample_parquet_file):
    """Test successful Parquet ingestion."""

    file_path, expected_dataframe = sample_parquet_file

    actual_dataframe = load_parquet(file_path)

    assert_frame_equal(actual_dataframe, expected_dataframe)


def test_load_parquet_with_string_path(sample_parquet_file):
    """Test Parquet ingestion using a string path."""

    file_path, expected_dataframe = sample_parquet_file

    actual_dataframe = load_parquet(str(file_path))

    assert_frame_equal(actual_dataframe, expected_dataframe)


def test_load_parquet_with_selected_columns(sample_parquet_file):
    """Test loading selected columns from a Parquet file."""

    file_path, _ = sample_parquet_file

    dataframe = load_parquet(
        file_path,
        columns=["product", "price"],
    )

    assert list(dataframe.columns) == ["product", "price"]
    assert len(dataframe) == 3


def test_load_parquet_file_not_found(tmp_path):
    """Test missing Parquet file handling."""

    file_path = tmp_path / "missing.parquet"

    with pytest.raises(FileNotFoundError):
        load_parquet(file_path)


def test_load_parquet_directory_error(tmp_path):
    """Test directory path handling."""

    with pytest.raises(IsADirectoryError):
        load_parquet(tmp_path)


def test_load_parquet_invalid_extension(tmp_path):
    """Test unsupported file extension handling."""

    file_path = tmp_path / "data.csv"

    file_path.write_text(
        "product,price\nLaptop,75000",
        encoding="utf-8",
    )

    with pytest.raises(UnsupportedFileFormatError):
        load_parquet(file_path)


def test_load_parquet_invalid_content(tmp_path):
    """Test invalid Parquet content handling."""

    file_path = tmp_path / "invalid.parquet"

    file_path.write_text(
        "This is not a valid Parquet file.",
        encoding="utf-8",
    )

    with pytest.raises(pyarrow.ArrowInvalid):
        load_parquet(file_path)
