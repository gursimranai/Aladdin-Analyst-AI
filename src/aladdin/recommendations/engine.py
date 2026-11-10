import pandas as pd

from aladdin.cleaning.models import MissingValueStrategy
from aladdin.logging_config import get_logger
from aladdin.quality.assessor import assess_data_quality
from aladdin.quality.models import DataQualityIssue
from aladdin.recommendations.models import (
    CleaningRecommendation,
    RecommendationAction,
    RecommendationPriority,
    RecommendationReport,
)

logger = get_logger("recommendations.engine")


def _recommend_missing_value_handling(
    dataframe: pd.DataFrame,
    issue: DataQualityIssue,
) -> CleaningRecommendation:
    """Generate a recommendation for a column containing missing values."""

    column_name = issue.column_name
    series = dataframe[column_name]

    missing_count = issue.affected_count or 0

    if series.isna().all():
        return CleaningRecommendation(
            code=f"MISSING_VALUES_{column_name}",
            title=f"Review missing values in '{column_name}'",
            description=(
                f"Column '{column_name}' contains only missing values. "
                "A filling strategy cannot be reliably determined automatically."
            ),
            action=RecommendationAction.MANUAL_REVIEW,
            priority=RecommendationPriority.HIGH,
            column_name=column_name,
            affected_count=missing_count,
        )

    if pd.api.types.is_numeric_dtype(series.dtype) and not pd.api.types.is_bool_dtype(
        series.dtype
    ):
        strategy = MissingValueStrategy.FILL_MEDIAN
        strategy_name = "median"
    else:
        strategy = MissingValueStrategy.FILL_MODE
        strategy_name = "mode"

    return CleaningRecommendation(
        code=f"MISSING_VALUES_{column_name}",
        title=f"Handle missing values in '{column_name}'",
        description=(
            f"Column '{column_name}' contains {missing_count} missing values. "
            f"Consider filling them using the column's {strategy_name}."
        ),
        action=RecommendationAction.FILL_MISSING_VALUES,
        priority=RecommendationPriority.MEDIUM,
        column_name=column_name,
        affected_count=missing_count,
        suggested_strategy=strategy,
    )


def _generate_recommendation(
    dataframe: pd.DataFrame,
    issue: DataQualityIssue,
) -> CleaningRecommendation | None:
    """Convert an individual quality issue into a recommendation."""

    if issue.code == "MISSING_VALUES":
        return _recommend_missing_value_handling(dataframe, issue)

    if issue.code == "DUPLICATE_ROWS":
        return CleaningRecommendation(
            code="DUPLICATE_ROWS",
            title="Remove duplicate rows",
            description=(
                f"The dataset contains {issue.affected_count} duplicate rows. "
                "Consider removing exact duplicate records."
            ),
            action=RecommendationAction.DROP_DUPLICATE_ROWS,
            priority=RecommendationPriority.MEDIUM,
            affected_count=issue.affected_count,
        )

    if issue.code == "CONSTANT_COLUMN":
        return CleaningRecommendation(
            code=f"CONSTANT_COLUMN_{issue.column_name}",
            title=f"Review constant column '{issue.column_name}'",
            description=(
                f"Column '{issue.column_name}' contains only one distinct "
                "non-null value. Consider removing it if it has no "
                "business or domain significance."
            ),
            action=RecommendationAction.DROP_CONSTANT_COLUMN,
            priority=RecommendationPriority.LOW,
            column_name=issue.column_name,
            affected_count=issue.affected_count,
        )

    return None


def recommend_cleaning(dataframe: pd.DataFrame) -> RecommendationReport:
    """
    Generate data cleaning recommendations without modifying the dataset.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Dataset to inspect.

    Returns
    -------
    RecommendationReport
        Recommendations based on detected data quality issues.

    Raises
    ------
    TypeError
        If the input is not a Pandas DataFrame.
    """

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")

    logger.info(
        "Generating cleaning recommendations | rows=%d | columns=%d",
        len(dataframe),
        len(dataframe.columns),
    )

    quality_report = assess_data_quality(dataframe)

    recommendations: list[CleaningRecommendation] = []

    # Structural problems require manual review.
    if any(issue.code == "EMPTY_DATASET" for issue in quality_report.issues):
        recommendations.append(
            CleaningRecommendation(
                code="REVIEW_EMPTY_DATASET",
                title="Review empty dataset",
                description=(
                    "The dataset contains no rows or no columns. "
                    "Verify the source data before attempting cleaning."
                ),
                action=RecommendationAction.MANUAL_REVIEW,
                priority=RecommendationPriority.HIGH,
                affected_count=0,
            )
        )

        return RecommendationReport(
            row_count=quality_report.row_count,
            column_count=quality_report.column_count,
            recommendations=recommendations,
        )

    duplicate_column_names = any(
        issue.code == "DUPLICATE_COLUMN_NAMES" for issue in quality_report.issues
    )

    if duplicate_column_names:
        recommendations.append(
            CleaningRecommendation(
                code="REVIEW_DUPLICATE_COLUMN_NAMES",
                title="Resolve duplicate column names",
                description=(
                    "The dataset contains duplicate column names. "
                    "Rename the affected columns before applying "
                    "column-specific cleaning recommendations."
                ),
                action=RecommendationAction.MANUAL_REVIEW,
                priority=RecommendationPriority.HIGH,
                affected_count=sum(
                    issue.affected_count or 0
                    for issue in quality_report.issues
                    if issue.code == "DUPLICATE_COLUMN_NAMES"
                ),
            )
        )

    for issue in quality_report.issues:
        # Column-specific recommendations are unsafe when labels
        # are ambiguous.
        if duplicate_column_names and issue.column_name is not None:
            continue

        recommendation = _generate_recommendation(dataframe, issue)

        if recommendation is not None:
            recommendations.append(recommendation)

    report = RecommendationReport(
        row_count=quality_report.row_count,
        column_count=quality_report.column_count,
        recommendations=recommendations,
    )

    logger.info(
        "Recommendation generation completed | recommendations=%d",
        len(report.recommendations),
    )

    return report
