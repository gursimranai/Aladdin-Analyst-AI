import pandas as pd

from aladdin.logging_config import get_logger
from aladdin.quality.models import (
    DataQualityIssue,
    DataQualityReport,
    IssueSeverity,
)

logger = get_logger("quality.assessor")


def assess_data_quality(dataframe: pd.DataFrame) -> DataQualityReport:
    """
    Assess the quality of a Pandas DataFrame.

    Checks for missing values, duplicate rows, constant columns,
    duplicate column names, and empty datasets.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Dataset to assess.

    Returns
    -------
    DataQualityReport
        Structured report containing detected quality issues.

    Raises
    ------
    TypeError
        If the input is not a Pandas DataFrame.
    """

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")

    row_count, column_count = dataframe.shape

    logger.info(
        "Starting data quality assessment | rows=%d | columns=%d",
        row_count,
        column_count,
    )

    issues: list[DataQualityIssue] = []

    # Check for an empty dataset.
    if row_count == 0 or column_count == 0:
        issues.append(
            DataQualityIssue(
                code="EMPTY_DATASET",
                severity=IssueSeverity.ERROR,
                message=("Dataset contains no rows or no columns."),
                affected_count=0,
            )
        )

    # Check for duplicate column names.
    duplicate_mask = dataframe.columns.duplicated(keep=False)

    if duplicate_mask.any():
        duplicate_columns = list(
            dict.fromkeys(str(name) for name in dataframe.columns[duplicate_mask])
        )

        issues.append(
            DataQualityIssue(
                code="DUPLICATE_COLUMN_NAMES",
                severity=IssueSeverity.ERROR,
                message="Dataset contains duplicate column names.",
                affected_count=len(duplicate_columns),
                affected_columns=duplicate_columns,
            )
        )

    # Check individual columns.
    for position, column_name in enumerate(dataframe.columns):
        series = dataframe.iloc[:, position]

        missing_count = int(series.isna().sum())

        # Check for missing values.
        if missing_count > 0:
            missing_percentage = missing_count / row_count * 100 if row_count else 0.0

            issues.append(
                DataQualityIssue(
                    code="MISSING_VALUES",
                    severity=IssueSeverity.WARNING,
                    message=(
                        f"Column '{column_name}' contains "
                        f"{missing_count} missing values "
                        f"({missing_percentage:.2f}%)."
                    ),
                    column_name=str(column_name),
                    affected_count=missing_count,
                )
            )

        # Check for constant columns.
        non_null_count = int(series.count())

        if non_null_count > 0 and series.nunique(dropna=True) == 1:
            issues.append(
                DataQualityIssue(
                    code="CONSTANT_COLUMN",
                    severity=IssueSeverity.INFO,
                    message=(
                        f"Column '{column_name}' contains "
                        "only one distinct non-null value."
                    ),
                    column_name=str(column_name),
                    affected_count=non_null_count,
                )
            )

    # Check for duplicate rows.
    if column_count > 0:
        duplicate_rows = int(dataframe.duplicated().sum())

        if duplicate_rows > 0:
            issues.append(
                DataQualityIssue(
                    code="DUPLICATE_ROWS",
                    severity=IssueSeverity.WARNING,
                    message=(f"Dataset contains {duplicate_rows} duplicate rows."),
                    affected_count=duplicate_rows,
                )
            )

    report = DataQualityReport(
        row_count=row_count,
        column_count=column_count,
        issues=issues,
    )

    logger.info(
        "Data quality assessment completed | issues=%d | errors=%s",
        len(report.issues),
        report.has_errors,
    )

    return report
