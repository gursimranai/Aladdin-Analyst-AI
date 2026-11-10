import pandas as pd
import pytest

from aladdin.insights import InsightCategory, InsightPriority, generate_insights


def _get_relationship_insights(dataframe: pd.DataFrame):
    report = generate_insights(dataframe)

    return [
        insight
        for insight in report.insights
        if insight.category == InsightCategory.RELATIONSHIP
    ]


def test_detects_strong_positive_correlation():
    dataframe = pd.DataFrame(
        {
            "advertising": [1, 2, 3, 4, 5],
            "revenue": [2, 4, 6, 8, 10],
        }
    )

    insights = _get_relationship_insights(dataframe)

    assert len(insights) == 1
    assert insights[0].priority == InsightPriority.HIGH
    assert insights[0].evidence["correlation"] == pytest.approx(1.0)
    assert insights[0].evidence["method"] == "pearson"


def test_detects_strong_negative_correlation():
    dataframe = pd.DataFrame(
        {
            "discount": [1, 2, 3, 4, 5],
            "profit": [10, 8, 6, 4, 2],
        }
    )

    insights = _get_relationship_insights(dataframe)

    assert len(insights) == 1
    assert insights[0].evidence["correlation"] == pytest.approx(-1.0)
    assert "NEGATIVE" in insights[0].code


def test_does_not_report_weak_correlation():
    dataframe = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "y": [1, 4, 2, 5, 3],
        }
    )

    assert _get_relationship_insights(dataframe) == []


def test_handles_missing_values_pairwise():
    dataframe = pd.DataFrame(
        {
            "x": [1, 2, 3, 4],
            "y": [2, None, 6, 8],
        }
    )

    insights = _get_relationship_insights(dataframe)

    assert len(insights) == 1
    assert insights[0].evidence["observations"] == 3


def test_skips_constant_columns():
    dataframe = pd.DataFrame(
        {
            "constant": [5, 5, 5, 5],
            "value": [1, 2, 3, 4],
        }
    )

    assert _get_relationship_insights(dataframe) == []


def test_skips_pairs_with_insufficient_observations():
    dataframe = pd.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [2, None, None],
        }
    )

    assert _get_relationship_insights(dataframe) == []


def test_excludes_boolean_columns():
    dataframe = pd.DataFrame(
        {
            "numeric": [1, 2, 3, 4],
            "flag": [True, False, True, False],
        }
    )

    assert _get_relationship_insights(dataframe) == []


def test_does_not_duplicate_relationship_pairs():
    dataframe = pd.DataFrame(
        {
            "a": [1, 2, 3, 4],
            "b": [2, 4, 6, 8],
            "c": [4, 3, 2, 1],
        }
    )

    insights = _get_relationship_insights(dataframe)

    pairs = [tuple(insight.evidence["columns"]) for insight in insights]

    assert len(pairs) == len(set(pairs))
    assert len(insights) == 3


def test_skips_relationship_analysis_for_duplicate_column_names():
    dataframe = pd.DataFrame(
        [[1, 2], [2, 4], [3, 6]],
        columns=["value", "value"],
    )

    assert _get_relationship_insights(dataframe) == []


def test_does_not_modify_original_dataframe():
    dataframe = pd.DataFrame(
        {
            "x": [1, 2, 3, 4],
            "y": [2, 4, 6, 8],
        }
    )

    original = dataframe.copy(deep=True)

    _get_relationship_insights(dataframe)

    pd.testing.assert_frame_equal(dataframe, original)


def test_detects_correlation_at_threshold_boundary():
    dataframe = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "y": [1, 3, 2, 5, 4],
        }
    )

    insights = _get_relationship_insights(dataframe)

    assert len(insights) == 1
    assert insights[0].evidence["correlation"] == pytest.approx(0.80)
    assert insights[0].priority == InsightPriority.MEDIUM


def test_handles_infinite_values_using_finite_observations():
    dataframe = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, float("inf"), 8, 10],
        }
    )

    insights = _get_relationship_insights(dataframe)

    assert len(insights) == 1
    assert insights[0].evidence["correlation"] == pytest.approx(1.0)
    assert insights[0].evidence["observations"] == 4
