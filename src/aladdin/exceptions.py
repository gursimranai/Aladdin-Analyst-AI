class AladdinError(Exception):
    """Base exception for all Aladdin Analyst AI errors."""


class DataIngestionError(AladdinError):
    """Base exception for data ingestion errors."""


class UnsupportedFileFormatError(DataIngestionError, ValueError):
    """Raised when an unsupported file format is provided."""
