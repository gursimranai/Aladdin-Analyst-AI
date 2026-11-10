import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from aladdin.exceptions import UnsupportedFileFormatError
from aladdin.ingestion import load_data


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for ingestion tests."""

    return pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "price": [75000, 1200, 2500],
        }
    )


@pytest.fixture
def sample_files(tmp_path, sample_dataframe):
    """Create sample files in all supported formats."""

    csv_file = tmp_path / "sales.csv"
    excel_file = tmp_path / "sales.xlsx"
    json_file = tmp_path / "sales.json"
    parquet_file = tmp_path / "sales.parquet"

    sample_dataframe.to_csv(csv_file, index=False)
    sample_dataframe.to_excel(excel_file, index=False)
    sample_dataframe.to_json(json_file, orient="records")
    sample_dataframe.to_parquet(parquet_file, index=False)

    return {
        ".csv": csv_file,
        ".xlsx": excel_file,
        ".json": json_file,
        ".parquet": parquet_file,
    }


@pytest.mark.parametrize(
    "extension",
    [".csv", ".xlsx", ".json", ".parquet"],
)
def test_load_data_detects_file_format(
    extension,
    sample_files,
    sample_dataframe,
):
    """Test automatic detection of supported file formats."""

    actual_dataframe = (
        load_data(
            sample_files[extension],
            orient="records" if extension == ".json" else None,
        )
        if extension == ".json"
        else load_data(sample_files[extension])
    )

    assert_frame_equal(actual_dataframe, sample_dataframe)


def test_load_data_with_string_path(sample_files, sample_dataframe):
    """Test unified ingestion using a string path."""

    actual_dataframe = load_data(str(sample_files[".csv"]))

    assert_frame_equal(actual_dataframe, sample_dataframe)


def test_load_data_with_case_insensitive_extension(tmp_path, sample_dataframe):
    """Test that uppercase file extensions are supported."""

    file_path = tmp_path / "sales.CSV"

    sample_dataframe.to_csv(file_path, index=False)

    actual_dataframe = load_data(file_path)

    assert_frame_equal(actual_dataframe, sample_dataframe)


def test_load_data_with_loader_arguments(tmp_path, sample_dataframe):
    """Test that loader-specific arguments are forwarded."""

    file_path = tmp_path / "sales.csv"

    sample_dataframe.to_csv(file_path, index=False)

    actual_dataframe = load_data(
        file_path,
        usecols=["product"],
    )

    assert list(actual_dataframe.columns) == ["product"]
    assert len(actual_dataframe) == 3


def test_load_data_unsupported_format(tmp_path):
    """Test unsupported file format handling."""

    file_path = tmp_path / "sales.txt"

    file_path.write_text(
        "This is a text file.",
        encoding="utf-8",
    )

    with pytest.raises(UnsupportedFileFormatError):
        load_data(file_path)


def test_load_data_without_extension(tmp_path):
    """Test files without extensions."""

    file_path = tmp_path / "sales"

    file_path.write_text(
        "product,price\nLaptop,75000",
        encoding="utf-8",
    )

    with pytest.raises(UnsupportedFileFormatError):
        load_data(file_path)
