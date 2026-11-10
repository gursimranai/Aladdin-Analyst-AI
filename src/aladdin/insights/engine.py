import numpy as np
import pandas as pd

from aladdin.insights.models import (
    DataInsight,
    InsightCategory,
    InsightPriority,
    InsightReport,
)
from aladdin.logging_config import get_logger
from aladdin.profiling.profiler import profile_data

logger = get_logger("insights.engine")

DOMINANT_CATEGORY_THRESHOLD = 80.0
HIGH_CARDINALITY_THRESHOLD = 50
SKEWNESS_THRESHOLD = 1.0
IQR_MULTIPLIER = 1.5
CORRELATION_THRESHOLD = 0.80
MIN_CORRELATION_SAMPLES = 3
CORRELATION_TOLERANCE = 1e-12


def _is_numeric(series: pd.Series) -> bool:
    """Return whether a column contains non-boolean numeric data."""

    return pd.api.types.is_numeric_dtype(
        series.dtype
    ) and not pd.api.types.is_bool_dtype(series.dtype)


def _is_categorical(series: pd.Series) -> bool:
    """Return whether a column has a categorical data type."""

    return (
        pd.api.types.is_object_dtype(series.dtype)
        or pd.api.types.is_string_dtype(series.dtype)
        or isinstance(series.dtype, pd.CategoricalDtype)
    )


def _analyze_missing_values(
    column_name: str,
    missing_count: int,
    missing_percentage: float,
) -> DataInsight | None:
    """Generate an insight when a column contains missing values."""

    if missing_count == 0:
        return None

    priority = (
        InsightPriority.HIGH if missing_percentage >= 20 else InsightPriority.MEDIUM
    )

    return DataInsight(
        code=f"MISSING_VALUES_{column_name}",
        title=f"Missing values detected in '{column_name}'",
        description=(
            f"Column '{column_name}' contains {missing_count} missing values "
            f"({missing_percentage:.2f}% of its rows)."
        ),
        category=InsightCategory.DATA_QUALITY,
        priority=priority,
        column_name=column_name,
        evidence={
            "missing_count": missing_count,
            "missing_percentage": missing_percentage,
        },
    )


def _analyze_categorical_column(
    column_name: str,
    series: pd.Series,
    unique_count: int,
) -> list[DataInsight]:
    """Generate insights for categorical columns."""

    insights = []

    if unique_count > HIGH_CARDINALITY_THRESHOLD:
        insights.append(
            DataInsight(
                code=f"HIGH_CARDINALITY_{column_name}",
                title=f"High cardinality in '{column_name}'",
                description=(
                    f"Column '{column_name}' contains {unique_count} "
                    "distinct values. Consider whether it represents "
                    "identifiers or free-text data."
                ),
                category=InsightCategory.CATEGORICAL,
                priority=InsightPriority.LOW,
                column_name=column_name,
                evidence={"unique_count": unique_count},
            )
        )

    value_counts = series.value_counts(normalize=True, dropna=True)

    if not value_counts.empty:
        dominant_percentage = float(value_counts.iloc[0] * 100)
        dominant_value = value_counts.index[0]

        if dominant_percentage >= DOMINANT_CATEGORY_THRESHOLD:
            insights.append(
                DataInsight(
                    code=f"DOMINANT_CATEGORY_{column_name}",
                    title=f"Dominant category in '{column_name}'",
                    description=(
                        f"Value '{dominant_value}' represents "
                        f"{dominant_percentage:.2f}% of non-missing "
                        f"values in '{column_name}'."
                    ),
                    category=InsightCategory.CATEGORICAL,
                    priority=InsightPriority.MEDIUM,
                    column_name=column_name,
                    evidence={
                        "dominant_value": str(dominant_value),
                        "dominant_percentage": dominant_percentage,
                    },
                )
            )

    return insights


def _analyze_numeric_column(
    column_name: str,
    series: pd.Series,
) -> list[DataInsight]:
    """Generate distribution and outlier insights for numeric columns."""

    insights = []
    values = series.dropna()
    values = values[np.isfinite(values)]

    if len(values) < 4:
        return insights

    # Analyze potential outliers using the IQR method.
    q1 = float(values.quantile(0.25))
    q3 = float(values.quantile(0.75))
    iqr = q3 - q1

    lower_bound = q1 - IQR_MULTIPLIER * iqr
    upper_bound = q3 + IQR_MULTIPLIER * iqr

    outliers = values[(values < lower_bound) | (values > upper_bound)]

    if not outliers.empty:
        outlier_count = len(outliers)
        outlier_percentage = outlier_count / len(values) * 100

        insights.append(
            DataInsight(
                code=f"POTENTIAL_OUTLIERS_{column_name}",
                title=f"Potential outliers in '{column_name}'",
                description=(
                    f"Column '{column_name}' contains {outlier_count} "
                    f"potential outliers ({outlier_percentage:.2f}%). "
                    "These observations fall outside the IQR bounds."
                ),
                category=InsightCategory.DISTRIBUTION,
                priority=(
                    InsightPriority.HIGH
                    if outlier_percentage >= 10
                    else InsightPriority.MEDIUM
                ),
                column_name=column_name,
                evidence={
                    "outlier_count": outlier_count,
                    "outlier_percentage": outlier_percentage,
                    "q1": q1,
                    "q3": q3,
                    "iqr": iqr,
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                },
            )
        )

    # Analyze distribution skewness.
    skewness = values.skew()

    if pd.notna(skewness) and abs(float(skewness)) > SKEWNESS_THRESHOLD:
        skewness = float(skewness)

        direction = "right-skewed" if skewness > 0 else "left-skewed"

        insights.append(
            DataInsight(
                code=f"SKEWED_DISTRIBUTION_{column_name}",
                title=f"Skewed distribution in '{column_name}'",
                description=(
                    f"Column '{column_name}' has a {direction} distribution "
                    f"with a skewness of {skewness:.2f}."
                ),
                category=InsightCategory.DISTRIBUTION,
                priority=InsightPriority.MEDIUM,
                column_name=column_name,
                evidence={"skewness": skewness},
            )
        )

    return insights


def generate_insights(dataframe: pd.DataFrame) -> InsightReport:
    """
    Generate deterministic analytical insights from a DataFrame.

    The original DataFrame is never modified.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Dataset to analyze.

    Returns
    -------
    InsightReport
        Structured analytical findings.

    Raises
    ------
    TypeError
        If the input is not a Pandas DataFrame.
    """

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")

    logger.info(
        "Generating analytical insights | rows=%d | columns=%d",
        len(dataframe),
        len(dataframe.columns),
    )

    profile = profile_data(dataframe, top_n=1)
    insights: list[DataInsight] = []

    # Duplicate labels make column-specific identification ambiguous.
    if dataframe.columns.has_duplicates:
        logger.warning(
            "Skipping column-specific insights due to duplicate column names."
        )

        return InsightReport(
            row_count=profile.row_count,
            column_count=profile.column_count,
        )

    for position, column_profile in enumerate(profile.columns):
        series = dataframe.iloc[:, position]
        column_name = column_profile.name

        # Missing-value insights apply to all column types.
        missing_insight = _analyze_missing_values(
            column_name,
            column_profile.missing_count,
            column_profile.missing_percentage,
        )

        if missing_insight is not None:
            insights.append(missing_insight)

        # Skip distribution and categorical analysis for empty columns.
        if column_profile.non_null_count == 0:
            continue

        if _is_numeric(series):
            insights.extend(_analyze_numeric_column(column_name, series))

        elif _is_categorical(series):
            insights.extend(
                _analyze_categorical_column(
                    column_name,
                    series,
                    column_profile.unique_count,
                )
            )

    insights.extend(_analyze_correlations(dataframe))

    report = InsightReport(
        row_count=profile.row_count,
        column_count=profile.column_count,
        insights=insights,
    )

    logger.info(
        "Insight generation completed | insights=%d | high_priority=%d",
        report.insight_count,
        report.high_priority_count,
    )

    return report


def _analyze_correlations(dataframe: pd.DataFrame) -> list[DataInsight]:
    """Identify strong Pearson correlations between numeric columns."""

    numeric_columns = [
        column for column in dataframe.columns if _is_numeric(dataframe[column])
    ]

    insights: list[DataInsight] = []

    # Analyze each unique pair exactly once.
    for i, first_column in enumerate(numeric_columns):
        for second_column in numeric_columns[i + 1 :]:
            # Use pairwise complete observations.
            paired_data = dataframe[[first_column, second_column]].dropna()

            # Exclude positive and negative infinity.
            finite_mask = np.isfinite(paired_data.to_numpy(dtype=float)).all(axis=1)

            paired_data = paired_data.loc[finite_mask]

            if len(paired_data) < MIN_CORRELATION_SAMPLES:
                continue

            # Constant columns cannot produce meaningful correlations.
            if (
                paired_data[first_column].nunique() < 2
                or paired_data[second_column].nunique() < 2
            ):
                continue

            correlation = float(
                paired_data[first_column].corr(
                    paired_data[second_column],
                    method="pearson",
                )
            )

            if pd.isna(correlation):
                continue

            absolute_correlation = abs(correlation)

            if absolute_correlation + CORRELATION_TOLERANCE < CORRELATION_THRESHOLD:
                continue

            direction = "POSITIVE" if correlation > 0 else "NEGATIVE"

            priority = (
                InsightPriority.HIGH
                if absolute_correlation >= 0.90
                else InsightPriority.MEDIUM
            )

            insights.append(
                DataInsight(
                    code=(
                        f"STRONG_{direction}_CORRELATION_{first_column}_{second_column}"
                    ),
                    title=f"Strong {direction.lower()} correlation",
                    description=(
                        f"Columns '{first_column}' and '{second_column}' "
                        f"have a {direction.lower()} Pearson correlation "
                        f"of {correlation:.3f}. This indicates a strong "
                        "linear association, not causation."
                    ),
                    category=InsightCategory.RELATIONSHIP,
                    priority=priority,
                    evidence={
                        "columns": [first_column, second_column],
                        "method": "pearson",
                        "correlation": correlation,
                        "absolute_correlation": absolute_correlation,
                        "observations": len(paired_data),
                        "threshold": CORRELATION_THRESHOLD,
                    },
                )
            )

    # Present the strongest relationships first.
    insights.sort(
        key=lambda insight: insight.evidence["absolute_correlation"],
        reverse=True,
    )

    return insights
