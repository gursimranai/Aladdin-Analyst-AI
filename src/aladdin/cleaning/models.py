from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import pandas as pd


class MissingValueStrategy(StrEnum):
    """Available strategies for handling missing values."""

    KEEP = "keep"
    DROP_ROWS = "drop_rows"
    FILL_VALUE = "fill_value"
    FILL_MEAN = "fill_mean"
    FILL_MEDIAN = "fill_median"
    FILL_MODE = "fill_mode"


@dataclass
class MissingValueConfig:
    """Configuration for handling missing values in a column."""

    strategy: MissingValueStrategy = MissingValueStrategy.KEEP
    value: Any = None

    def __post_init__(self) -> None:
        if not isinstance(self.strategy, MissingValueStrategy):
            raise TypeError("strategy must be a MissingValueStrategy.")

        if self.strategy == MissingValueStrategy.FILL_VALUE and self.value is None:
            raise ValueError("A non-None value is required for FILL_VALUE.")


@dataclass
class CleaningConfig:
    """Configuration controlling dataset cleaning operations."""

    missing_values: dict[str, MissingValueConfig] = field(default_factory=dict)

    drop_duplicate_rows: bool = False
    drop_constant_columns: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.missing_values, dict):
            raise TypeError("missing_values must be a dictionary.")

        for column_name, config in self.missing_values.items():
            if not isinstance(column_name, str):
                raise TypeError("Missing-value configuration keys must be strings.")

            if not isinstance(config, MissingValueConfig):
                raise TypeError(
                    "Each missing_values entry must be a MissingValueConfig instance."
                )

        if not isinstance(self.drop_duplicate_rows, bool):
            raise TypeError("drop_duplicate_rows must be a boolean.")

        if not isinstance(self.drop_constant_columns, bool):
            raise TypeError("drop_constant_columns must be a boolean.")


@dataclass
class CleaningReport:
    """Summary of the changes made during dataset cleaning."""

    rows_before: int
    rows_after: int

    columns_before: int
    columns_after: int

    missing_values_before: int
    missing_values_after: int

    missing_values_filled: int = 0
    rows_removed_for_missing_values: int = 0
    duplicate_rows_removed: int = 0

    constant_columns_removed: list[str] = field(default_factory=list)


@dataclass
class CleaningResult:
    """Contains the cleaned dataset and its cleaning report."""

    dataframe: pd.DataFrame
    report: CleaningReport
