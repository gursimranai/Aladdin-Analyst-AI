from aladdin.exceptions import (
    AladdinError,
    DataIngestionError,
    UnsupportedFileFormatError,
)


def test_aladdin_error_is_base_exception():
    """Test the root exception hierarchy."""

    assert issubclass(AladdinError, Exception)


def test_data_ingestion_error_inherits_from_aladdin_error():
    """Test ingestion exception inheritance."""

    assert issubclass(DataIngestionError, AladdinError)


def test_unsupported_format_error_inherits_from_ingestion_error():
    """Test unsupported format exception inheritance."""

    assert issubclass(UnsupportedFileFormatError, DataIngestionError)


def test_unsupported_format_error_is_also_value_error():
    """Test backward compatibility with ValueError."""

    assert issubclass(UnsupportedFileFormatError, ValueError)
