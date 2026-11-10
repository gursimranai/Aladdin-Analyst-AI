from dataclasses import dataclass, field
from typing import Any


@dataclass
class ColumnProfile:
    """Profiling information for a single DataFrame column."""

    name: str
    dtype: str

    non_null_count: int
    missing_count: int
    missing_percentage: float

    unique_count: int
    unique_percentage: float

    mean: float | None = None
    median: float | None = None
    std: float | None = None
    min_value: float | None = None
    max_value: float | None = None

    top_values: list[tuple[Any, int]] = field(default_factory=list)


@dataclass
class DataProfile:
    """Summary of a complete DataFrame."""

    row_count: int
    column_count: int
    duplicate_rows: int

    columns: list[ColumnProfile]
