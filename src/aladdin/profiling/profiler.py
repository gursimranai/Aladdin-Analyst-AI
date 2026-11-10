from typing import Any

import numpy as np
import pandas as pd

from aladdin.logging_config import get_logger
from aladdin.profiling.models import ColumnProfile, DataProfile

logger = get_logger("profiling.profiler")


def _safe_float(value: Any) -> float | None:
    """Convert a finite numeric value to float, returning None otherwise."""

    if pd.isna(value) or not np.isfinite(value):
        return None

    return float(value)


def profile_data(
    dataframe: pd.DataFrame,
    top_n: int = 5,
) -> DataProfile:
    """
    Generate a statistical profile of a Pandas DataFrame.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Dataset to profile.

    top_n : int
        Number of most frequent values to include for non-numeric columns.

    Returns
    -------
    DataProfile
        Structured dataset and column profiling information.

    Raises
    ------
    TypeError
        If the input is not a Pandas DataFrame or top_n is not an integer.

    ValueError
        If top_n is less than or equal to zero.
    """

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")

    if isinstance(top_n, bool) or not isinstance(top_n, int):
        raise TypeError("top_n must be an integer.")

    if top_n <= 0:
        raise ValueError("top_n must be greater than zero.")

    logger.info(
        "Starting dataset profiling | rows=%d | columns=%d",
        len(dataframe),
        len(dataframe.columns),
    )

    row_count, column_count = dataframe.shape

    column_profiles = []

    for position, column_name in enumerate(dataframe.columns):
        series = dataframe.iloc[:, position]

        non_null_count = int(series.count())
        missing_count = int(series.isna().sum())
        unique_count = int(series.nunique())

        missing_percentage = missing_count / row_count * 100 if row_count else 0.0

        unique_percentage = (
            unique_count / non_null_count * 100 if non_null_count else 0.0
        )

        column_profile = ColumnProfile(
            name=str(column_name),
            dtype=str(series.dtype),
            non_null_count=non_null_count,
            missing_count=missing_count,
            missing_percentage=missing_percentage,
            unique_count=unique_count,
            unique_percentage=unique_percentage,
        )

        is_numeric = pd.api.types.is_numeric_dtype(
            series.dtype
        ) and not pd.api.types.is_bool_dtype(series.dtype)

        if is_numeric:
            # Exclude missing and infinite values from numerical statistics.
            finite_series = series.replace([np.inf, -np.inf], np.nan).dropna()

            column_profile.mean = _safe_float(finite_series.mean())
            column_profile.median = _safe_float(finite_series.median())
            column_profile.std = _safe_float(finite_series.std())
            column_profile.min_value = _safe_float(finite_series.min())
            column_profile.max_value = _safe_float(finite_series.max())

        else:
            column_profile.top_values = [
                (value, int(count))
                for value, count in (
                    series.value_counts(dropna=True).head(top_n).items()
                )
            ]

        column_profiles.append(column_profile)

    duplicate_rows = int(dataframe.duplicated().sum())

    profile = DataProfile(
        row_count=row_count,
        column_count=column_count,
        duplicate_rows=duplicate_rows,
        columns=column_profiles,
    )

    logger.info(
        "Dataset profiling completed | rows=%d | columns=%d | duplicates=%d",
        profile.row_count,
        profile.column_count,
        profile.duplicate_rows,
    )

    return profile
