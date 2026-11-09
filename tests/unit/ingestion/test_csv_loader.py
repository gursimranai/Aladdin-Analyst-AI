import logging
from io import StringIO

import pandas as pd
import pytest
from pandas.errors import EmptyDataError
from pandas.testing import assert_frame_equal

from aladdin.exceptions import UnsupportedFileFormatError
from aladdin.ingestion.csv_loader import load_csv
from aladdin.logging_config import configure_logging, get_logger


def test_load_csv_successfully(tmp_path):
    """Test loading a valid CSV file."""

    csv_file = tmp_path / "sales.csv"

    csv_file.write_text(
        "product,price\nLaptop,50000\nPhone,20000\n",
        encoding="utf-8",
    )

    result = load_csv(csv_file)

    expected = pd.DataFrame(
        {
            "product": ["Laptop", "Phone"],
            "price": [50000, 20000],
        }
    )

    assert_frame_equal(result, expected)


def test_load_csv_with_string_path(tmp_path):
    """Test loading a CSV using a string path."""

    csv_file = tmp_path / "sales.csv"

    csv_file.write_text(
        "name,age\nAlice,22\n",
        encoding="utf-8",
    )

    result = load_csv(str(csv_file))

    assert result.shape == (1, 2)


def test_load_csv_with_custom_separator(tmp_path):
    """Test loading a CSV with a custom separator."""

    csv_file = tmp_path / "sales.csv"

    csv_file.write_text(
        "product;price\nLaptop;50000\nPhone;20000\n",
        encoding="utf-8",
    )

    result = load_csv(csv_file, sep=";")

    assert list(result.columns) == ["product", "price"]
    assert len(result) == 2


def test_load_csv_file_not_found(tmp_path):
    """Test handling a missing CSV file."""

    csv_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_csv(csv_file)


def test_load_csv_directory_error(tmp_path):
    """Test handling a directory instead of a file."""

    with pytest.raises(IsADirectoryError):
        load_csv(tmp_path)


def test_load_csv_invalid_extension(tmp_path):
    """Test rejecting files with unsupported extensions."""

    text_file = tmp_path / "data.txt"
    text_file.write_text("some data", encoding="utf-8")

    with pytest.raises(
        UnsupportedFileFormatError,
        match="Expected a .csv file",
    ):
        load_csv(text_file)


def test_load_empty_csv(tmp_path):
    """Test handling an empty CSV file."""

    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")

    with pytest.raises(EmptyDataError):
        load_csv(csv_file)


def test_load_csv_with_custom_encoding(tmp_path):
    """Test loading a CSV with a non-default encoding."""

    csv_file = tmp_path / "international.csv"

    csv_file.write_bytes("name,city\nAndré,Montréal\n".encode("cp1252"))

    result = load_csv(csv_file, encoding="cp1252")

    assert result.loc[0, "name"] == "André"
    assert result.loc[0, "city"] == "Montréal"


def test_load_csv_with_custom_missing_values(tmp_path):
    """Test recognizing custom missing-value representations."""

    csv_file = tmp_path / "missing_values.csv"

    csv_file.write_text(
        "product,price\nLaptop,50000\nMouse,MISSING\n",
        encoding="utf-8",
    )

    result = load_csv(csv_file, na_values=["MISSING"])

    assert pd.isna(result.loc[1, "price"])


def test_load_csv_with_selected_columns(tmp_path):
    """Test loading only selected columns."""

    csv_file = tmp_path / "sales.csv"

    csv_file.write_text(
        "product,quantity,price\nLaptop,2,75000\nMouse,5,1200\n",
        encoding="utf-8",
    )

    result = load_csv(csv_file, usecols=["product", "price"])

    assert list(result.columns) == ["product", "price"]
    assert result.shape == (2, 2)


def test_load_csv_logs_successful_ingestion(tmp_path):
    """Test that successful CSV ingestion produces useful logs."""

    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "product,price\nLaptop,50000\nMouse,500\n",
        encoding="utf-8",
    )

    configure_logging(level=logging.INFO)

    logger = get_logger("ingestion.csv_loader")

    output_stream = StringIO()
    handler = logging.StreamHandler(output_stream)

    previous_propagate = logger.propagate
    logger.addHandler(handler)
    logger.propagate = False

    try:
        dataframe = load_csv(csv_file)
        output = output_stream.getvalue()

    finally:
        logger.removeHandler(handler)
        handler.close()
        logger.propagate = previous_propagate

    assert len(dataframe) == 2
    assert len(dataframe.columns) == 2

    assert "Starting CSV ingestion" in output
    assert "Successfully loaded CSV" in output
    assert "rows=2" in output
    assert "columns=2" in output
