import pandas as pd
import pytest

from aladdin.cleaning.models import MissingValueStrategy
from aladdin.recommendations import (
    RecommendationAction,
    RecommendationPriority,
    recommend_cleaning,
)


def test_recommend_missing_numeric_values():
    dataframe = pd.DataFrame({"age": [20, None, 30, 40]})

    report = recommend_cleaning(dataframe)

    recommendation = report.recommendations[0]

    assert recommendation.action == RecommendationAction.FILL_MISSING_VALUES
    assert recommendation.suggested_strategy == MissingValueStrategy.FILL_MEDIAN
    assert recommendation.column_name == "age"
    assert recommendation.affected_count == 1


def test_recommend_missing_categorical_values():
    dataframe = pd.DataFrame({"city": ["Delhi", None, "Mumbai", "Delhi"]})

    report = recommend_cleaning(dataframe)

    recommendation = report.recommendations[0]

    assert recommendation.suggested_strategy == MissingValueStrategy.FILL_MODE
    assert recommendation.column_name == "city"


def test_all_null_column_requires_manual_review():
    dataframe = pd.DataFrame({"age": [None, None, None]})

    report = recommend_cleaning(dataframe)

    recommendation = report.recommendations[0]

    assert recommendation.action == RecommendationAction.MANUAL_REVIEW
    assert recommendation.priority == RecommendationPriority.HIGH
    assert recommendation.suggested_strategy is None


def test_recommend_duplicate_rows():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Alice"],
            "age": [20, 30, 20],
        }
    )

    report = recommend_cleaning(dataframe)

    recommendation = next(
        item
        for item in report.recommendations
        if item.action == RecommendationAction.DROP_DUPLICATE_ROWS
    )

    assert recommendation.affected_count == 1


def test_recommend_constant_column():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "source": ["CRM", "CRM", "CRM"],
        }
    )

    report = recommend_cleaning(dataframe)

    recommendation = next(
        item
        for item in report.recommendations
        if item.action == RecommendationAction.DROP_CONSTANT_COLUMN
    )

    assert recommendation.column_name == "source"
    assert recommendation.priority == RecommendationPriority.LOW


def test_empty_dataset_requires_manual_review():
    dataframe = pd.DataFrame()

    report = recommend_cleaning(dataframe)

    assert len(report.recommendations) == 1
    assert report.recommendations[0].action == RecommendationAction.MANUAL_REVIEW


def test_duplicate_column_names_require_manual_review():
    dataframe = pd.DataFrame(
        [[20, 30]],
        columns=["age", "age"],
    )

    report = recommend_cleaning(dataframe)

    assert len(report.recommendations) == 1
    assert report.recommendations[0].action == RecommendationAction.MANUAL_REVIEW


def test_recommendation_engine_does_not_modify_dataframe():
    dataframe = pd.DataFrame(
        {
            "age": [20, None, 30],
            "city": ["Delhi", "Mumbai", "Delhi"],
        }
    )

    original = dataframe.copy(deep=True)

    recommend_cleaning(dataframe)

    pd.testing.assert_frame_equal(dataframe, original)


def test_non_dataframe_input_raises_type_error():
    with pytest.raises(TypeError):
        recommend_cleaning([1, 2, 3])


def test_recommendation_report_contains_dataset_dimensions():
    dataframe = pd.DataFrame({"age": [20, None, 30]})

    report = recommend_cleaning(dataframe)

    assert report.row_count == 3
    assert report.column_count == 1
