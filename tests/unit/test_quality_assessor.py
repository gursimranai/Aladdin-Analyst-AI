import pandas as pd
import pytest

from aladdin.quality import (
    IssueSeverity,
    assess_data_quality,
)


@pytest.fixture
def clean_dataframe():
    """Create a dataset without quality issues."""

    return pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [22, 25, 30],
            "city": ["Delhi", "Mumbai", "Chandigarh"],
        }
    )


def test_assess_data_quality_returns_report(clean_dataframe):
    report = assess_data_quality(clean_dataframe)

    assert report.row_count == 3
    assert report.column_count == 3


def test_clean_dataframe_is_healthy(clean_dataframe):
    report = assess_data_quality(clean_dataframe)

    assert report.is_healthy is True
    assert report.has_errors is False
    assert report.has_warnings is False
    assert report.issues == []


def test_detects_missing_values():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None, "Charlie", None],
        }
    )

    report = assess_data_quality(dataframe)

    issue = report.issues[0]

    assert issue.code == "MISSING_VALUES"
    assert issue.severity == IssueSeverity.WARNING
    assert issue.column_name == "name"
    assert issue.affected_count == 2
    assert report.has_warnings is True


def test_detects_multiple_missing_value_columns():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None, "Charlie"],
            "age": [22, 25, None],
        }
    )

    report = assess_data_quality(dataframe)

    missing_issues = [
        issue for issue in report.issues if issue.code == "MISSING_VALUES"
    ]

    assert len(missing_issues) == 2


def test_detects_duplicate_rows():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Alice"],
            "age": [22, 25, 22],
        }
    )

    report = assess_data_quality(dataframe)

    issue = next(issue for issue in report.issues if issue.code == "DUPLICATE_ROWS")

    assert issue.severity == IssueSeverity.WARNING
    assert issue.affected_count == 1


def test_detects_constant_columns():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "country": ["India", "India", "India"],
        }
    )

    report = assess_data_quality(dataframe)

    issue = next(issue for issue in report.issues if issue.code == "CONSTANT_COLUMN")

    assert issue.severity == IssueSeverity.INFO
    assert issue.column_name == "country"
    assert issue.affected_count == 3


def test_constant_column_ignores_missing_values():
    dataframe = pd.DataFrame(
        {
            "category": ["A", "A", None],
        }
    )

    report = assess_data_quality(dataframe)

    constant_issues = [
        issue for issue in report.issues if issue.code == "CONSTANT_COLUMN"
    ]

    assert len(constant_issues) == 1


def test_all_missing_column_is_not_constant():
    dataframe = pd.DataFrame(
        {
            "value": [None, None, None],
        }
    )

    report = assess_data_quality(dataframe)

    codes = [issue.code for issue in report.issues]

    assert "MISSING_VALUES" in codes
    assert "CONSTANT_COLUMN" not in codes


def test_detects_duplicate_column_names():
    dataframe = pd.DataFrame(
        [["Alice", 22]],
        columns=["name", "name"],
    )

    report = assess_data_quality(dataframe)

    issue = next(
        issue for issue in report.issues if issue.code == "DUPLICATE_COLUMN_NAMES"
    )

    assert issue.severity == IssueSeverity.ERROR
    assert issue.affected_columns == ["name"]
    assert report.has_errors is True


def test_detects_empty_dataframe():
    dataframe = pd.DataFrame()

    report = assess_data_quality(dataframe)

    assert report.row_count == 0
    assert report.column_count == 0
    assert report.has_errors is True
    assert report.issues[0].code == "EMPTY_DATASET"


def test_detects_dataframe_without_rows():
    dataframe = pd.DataFrame(
        {
            "name": pd.Series(dtype="object"),
            "age": pd.Series(dtype="int64"),
        }
    )

    report = assess_data_quality(dataframe)

    assert report.row_count == 0
    assert report.column_count == 2
    assert report.has_errors is True


def test_detects_dataframe_without_columns():
    dataframe = pd.DataFrame(index=[0, 1, 2])

    report = assess_data_quality(dataframe)

    assert report.row_count == 3
    assert report.column_count == 0
    assert report.has_errors is True


def test_info_only_issues_do_not_make_dataset_unhealthy():
    dataframe = pd.DataFrame(
        {
            "country": ["India", "India", "India"],
            "id": [1, 2, 3],
        }
    )

    report = assess_data_quality(dataframe)

    assert report.has_warnings is False
    assert report.has_errors is False
    assert report.is_healthy is True

    assert len(report.issues) == 1
    assert report.issues[0].code == "CONSTANT_COLUMN"


def test_invalid_input():
    with pytest.raises(TypeError):
        assess_data_quality([1, 2, 3])


def test_assessment_does_not_modify_dataframe(clean_dataframe):
    original = clean_dataframe.copy(deep=True)

    assess_data_quality(clean_dataframe)

    pd.testing.assert_frame_equal(clean_dataframe, original)
