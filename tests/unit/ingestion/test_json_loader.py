import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from aladdin.exceptions import UnsupportedFileFormatError
from aladdin.ingestion.json_loader import load_json


@pytest.fixture
def sample_json_file(tmp_path):
    """Create a temporary JSON file for testing."""

    dataframe = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "price": [75000, 1200, 2500],
        }
    )

    file_path = tmp_path / "sales.json"

    dataframe.to_json(
        file_path,
        orient="records",
    )

    return file_path, dataframe


def test_load_json_successfully(sample_json_file):
    """Test successful JSON ingestion."""

    file_path, expected_dataframe = sample_json_file

    actual_dataframe = load_json(
        file_path,
        orient="records",
    )

    assert_frame_equal(actual_dataframe, expected_dataframe)


def test_load_json_with_string_path(sample_json_file):
    """Test JSON ingestion using a string path."""

    file_path, expected_dataframe = sample_json_file

    actual_dataframe = load_json(
        str(file_path),
        orient="records",
    )

    assert_frame_equal(actual_dataframe, expected_dataframe)


def test_load_json_lines_format(tmp_path):
    """Test JSON Lines ingestion."""

    file_path = tmp_path / "sales.json"

    file_path.write_text(
        '{"product":"Laptop","price":75000}\n{"product":"Mouse","price":1200}\n',
        encoding="utf-8",
    )

    dataframe = load_json(file_path, lines=True)

    assert len(dataframe) == 2
    assert list(dataframe.columns) == ["product", "price"]
    assert dataframe.iloc[0]["product"] == "Laptop"


def test_load_json_file_not_found(tmp_path):
    """Test missing JSON file handling."""

    file_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_json(file_path)


def test_load_json_directory_error(tmp_path):
    """Test directory path handling."""

    with pytest.raises(IsADirectoryError):
        load_json(tmp_path)


def test_load_json_invalid_extension(tmp_path):
    """Test unsupported file extension handling."""

    file_path = tmp_path / "data.csv"
    file_path.write_text(
        '[{"product":"Laptop"}]',
        encoding="utf-8",
    )

    with pytest.raises(UnsupportedFileFormatError):
        load_json(file_path)


def test_load_json_invalid_content(tmp_path):
    """Test invalid JSON content handling."""

    file_path = tmp_path / "invalid.json"
    file_path.write_text(
        "This is not valid JSON",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_json(file_path)
