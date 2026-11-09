import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from aladdin.exceptions import UnsupportedFileFormatError
from aladdin.ingestion.excel_loader import load_excel


@pytest.fixture
def sample_excel_file(tmp_path):
    """Create a temporary Excel file for testing."""

    dataframe = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "price": [75000, 1200, 2500],
        }
    )

    file_path = tmp_path / "sales.xlsx"

    dataframe.to_excel(
        file_path,
        index=False,
        engine="openpyxl",
    )

    return file_path, dataframe


def test_load_excel_successfully(sample_excel_file):
    """Test successful Excel ingestion."""

    file_path, expected_dataframe = sample_excel_file

    actual_dataframe = load_excel(file_path)

    assert_frame_equal(actual_dataframe, expected_dataframe)


def test_load_excel_with_string_path(sample_excel_file):
    """Test Excel ingestion using a string path."""

    file_path, expected_dataframe = sample_excel_file

    actual_dataframe = load_excel(str(file_path))

    assert_frame_equal(actual_dataframe, expected_dataframe)


def test_load_excel_with_selected_columns(sample_excel_file):
    """Test loading selected Excel columns."""

    file_path, _ = sample_excel_file

    dataframe = load_excel(
        file_path,
        usecols=["product"],
    )

    assert list(dataframe.columns) == ["product"]
    assert len(dataframe) == 3


def test_load_excel_with_selected_sheet(tmp_path):
    """Test loading a specific Excel worksheet."""

    file_path = tmp_path / "workbook.xlsx"

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        pd.DataFrame({"product": ["Laptop"]}).to_excel(
            writer,
            sheet_name="Products",
            index=False,
        )

        pd.DataFrame({"region": ["North"]}).to_excel(
            writer,
            sheet_name="Regions",
            index=False,
        )

    dataframe = load_excel(
        file_path,
        sheet_name="Regions",
    )

    assert list(dataframe.columns) == ["region"]
    assert dataframe.iloc[0]["region"] == "North"


def test_load_excel_file_not_found(tmp_path):
    """Test missing Excel file handling."""

    file_path = tmp_path / "missing.xlsx"

    with pytest.raises(FileNotFoundError):
        load_excel(file_path)


def test_load_excel_directory_error(tmp_path):
    """Test directory path handling."""

    with pytest.raises(IsADirectoryError):
        load_excel(tmp_path)


def test_load_excel_invalid_extension(tmp_path):
    """Test unsupported file extension handling."""

    file_path = tmp_path / "data.csv"
    file_path.write_text("product,price\nLaptop,75000")

    with pytest.raises(UnsupportedFileFormatError):
        load_excel(file_path)
