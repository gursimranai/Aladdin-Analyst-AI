import pandas as pd

from aladdin.cleaning.models import (
    CleaningConfig,
    CleaningReport,
    CleaningResult,
    MissingValueStrategy,
)
from aladdin.logging_config import get_logger

logger = get_logger("cleaning.cleaner")


def _validate_configuration(
    dataframe: pd.DataFrame,
    config: CleaningConfig,
) -> None:
    """Validate cleaning configuration against the dataset."""

    for column_name, column_config in config.missing_values.items():
        if column_name not in dataframe.columns:
            raise ValueError(f"Column '{column_name}' does not exist in the dataset.")

        if (dataframe.columns == column_name).sum() > 1:
            raise ValueError(
                f"Column '{column_name}' has duplicate column names. "
                "Cannot apply column-specific cleaning."
            )

        if column_config.strategy in {
            MissingValueStrategy.FILL_MEAN,
            MissingValueStrategy.FILL_MEDIAN,
        }:
            series = dataframe[column_name]

            if not pd.api.types.is_numeric_dtype(
                series.dtype
            ) or pd.api.types.is_bool_dtype(series.dtype):
                raise TypeError(
                    f"Strategy '{column_config.strategy.value}' "
                    f"requires a numeric column: '{column_name}'."
                )


def clean_data(
    dataframe: pd.DataFrame,
    config: CleaningConfig | None = None,
) -> CleaningResult:
    """
    Clean a Pandas DataFrame using an explicit configuration.

    The original DataFrame is never modified.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Dataset to clean.

    config : CleaningConfig | None
        Cleaning operations to execute. If omitted, no changes
        are applied.

    Returns
    -------
    CleaningResult
        Cleaned DataFrame and a summary of applied operations.

    Raises
    ------
    TypeError
        If the input or configuration has an invalid type.

    ValueError
        If a configured column does not exist or is ambiguous.
    """

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")

    if config is None:
        config = CleaningConfig()

    if not isinstance(config, CleaningConfig):
        raise TypeError("config must be a CleaningConfig instance.")

    _validate_configuration(dataframe, config)

    logger.info(
        "Starting data cleaning | rows=%d | columns=%d",
        len(dataframe),
        len(dataframe.columns),
    )

    # Work on a copy to protect the original dataset.
    cleaned = dataframe.copy(deep=True)

    rows_before, columns_before = cleaned.shape

    missing_values_before = int(cleaned.isna().sum().sum())

    missing_values_filled = 0
    rows_removed_for_missing_values = 0
    duplicate_rows_removed = 0
    constant_columns_removed: list[str] = []

    # Step 1: Handle missing values.
    columns_to_drop = [
        column_name
        for column_name, column_config in config.missing_values.items()
        if column_config.strategy == MissingValueStrategy.DROP_ROWS
    ]

    if columns_to_drop:
        rows_before_drop = len(cleaned)

        cleaned = cleaned.dropna(subset=columns_to_drop).copy()

        rows_removed_for_missing_values = rows_before_drop - len(cleaned)

    for column_name, column_config in config.missing_values.items():
        strategy = column_config.strategy

        if strategy in {
            MissingValueStrategy.KEEP,
            MissingValueStrategy.DROP_ROWS,
        }:
            continue

        series = cleaned[column_name]
        missing_before = int(series.isna().sum())

        if missing_before == 0:
            continue

        if strategy == MissingValueStrategy.FILL_VALUE:
            fill_value = column_config.value

        elif strategy == MissingValueStrategy.FILL_MEAN:
            fill_value = series.mean()

        elif strategy == MissingValueStrategy.FILL_MEDIAN:
            fill_value = series.median()

        elif strategy == MissingValueStrategy.FILL_MODE:
            modes = series.mode(dropna=True)

            if modes.empty:
                continue

            # Select the first mode for deterministic behavior.
            fill_value = modes.iloc[0]

        else:
            raise ValueError(f"Unsupported missing-value strategy: {strategy}")

        cleaned[column_name] = series.fillna(fill_value)

        missing_after = int(cleaned[column_name].isna().sum())

        missing_values_filled += missing_before - missing_after

    # Step 2: Remove duplicate rows.
    if config.drop_duplicate_rows:
        rows_before_deduplication = len(cleaned)

        cleaned = cleaned.drop_duplicates().copy()

        duplicate_rows_removed = rows_before_deduplication - len(cleaned)

    # Step 3: Remove constant columns.
    if config.drop_constant_columns:
        columns_to_keep = []

        for position, column_name in enumerate(cleaned.columns):
            series = cleaned.iloc[:, position]

            non_null_count = int(series.count())

            is_constant = non_null_count > 0 and series.nunique(dropna=True) == 1

            if is_constant:
                constant_columns_removed.append(str(column_name))
            else:
                columns_to_keep.append(position)

        cleaned = cleaned.iloc[:, columns_to_keep].copy()

    # Step 4: Generate the cleaning report.
    missing_values_after = int(cleaned.isna().sum().sum())

    report = CleaningReport(
        rows_before=rows_before,
        rows_after=len(cleaned),
        columns_before=columns_before,
        columns_after=len(cleaned.columns),
        missing_values_before=missing_values_before,
        missing_values_after=missing_values_after,
        missing_values_filled=missing_values_filled,
        rows_removed_for_missing_values=(rows_removed_for_missing_values),
        duplicate_rows_removed=duplicate_rows_removed,
        constant_columns_removed=constant_columns_removed,
    )

    logger.info(
        "Data cleaning completed | rows=%d | columns=%d | "
        "missing_filled=%d | duplicates_removed=%d",
        report.rows_after,
        report.columns_after,
        report.missing_values_filled,
        report.duplicate_rows_removed,
    )

    return CleaningResult(
        dataframe=cleaned,
        report=report,
    )
