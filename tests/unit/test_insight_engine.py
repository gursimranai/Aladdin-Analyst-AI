import pandas as pd
import pytest

from aladdin.insights import generate_insights
from aladdin.insights.models import InsightPriority


def get_insight_codes(report):
    return {insight.code for insight in report.insights}


def test_generate_insights_detects_missing_values():
    df = pd.DataFrame({"age": [20, 25, None, 30, 35]})

    report = generate_insights(df)

    assert "MISSING_VALUES_age" in get_insight_codes(report)


def test_missing_values_priority_is_high_at_20_percent():
    df = pd.DataFrame({"age": [20, None, 30, 40, 50]})

    report = generate_insights(df)

    insight = next(
        item for item in report.insights if item.code == "MISSING_VALUES_age"
    )

    assert insight.priority == InsightPriority.HIGH


def test_generate_insights_detects_potential_outliers():
    df = pd.DataFrame({"sales": [10, 11, 12, 13, 14, 100]})

    report = generate_insights(df)

    assert "POTENTIAL_OUTLIERS_sales" in get_insight_codes(report)


def test_generate_insights_detects_skewed_distribution():
    df = pd.DataFrame({"sales": [1, 2, 3, 4, 20]})

    report = generate_insights(df)

    assert "SKEWED_DISTRIBUTION_sales" in get_insight_codes(report)


def test_generate_insights_detects_dominant_category():
    df = pd.DataFrame({"city": ["Delhi", "Delhi", "Delhi", "Delhi", "Mumbai"]})

    report = generate_insights(df)

    assert "DOMINANT_CATEGORY_city" in get_insight_codes(report)


def test_generate_insights_detects_high_cardinality():
    df = pd.DataFrame({"category": [f"category_{i}" for i in range(51)]})

    report = generate_insights(df)

    assert "HIGH_CARDINALITY_category" in get_insight_codes(report)


def test_generate_insights_handles_boolean_columns():
    df = pd.DataFrame({"active": [True, False, True, False, True]})

    report = generate_insights(df)

    assert not any(insight.category.value == "numeric" for insight in report.insights)


def test_generate_insights_handles_all_null_columns():
    df = pd.DataFrame({"value": [None, None, None, None]})

    report = generate_insights(df)

    assert "MISSING_VALUES_value" in get_insight_codes(report)
    assert "POTENTIAL_OUTLIERS_value" not in get_insight_codes(report)
    assert "SKEWED_DISTRIBUTION_value" not in get_insight_codes(report)


def test_generate_insights_skips_small_numeric_samples():
    df = pd.DataFrame({"value": [10, 20, 30]})

    report = generate_insights(df)

    assert "POTENTIAL_OUTLIERS_value" not in get_insight_codes(report)
    assert "SKEWED_DISTRIBUTION_value" not in get_insight_codes(report)


def test_generate_insights_skips_duplicate_column_names():
    df = pd.DataFrame(
        [[10, 20], [30, 40]],
        columns=["value", "value"],
    )

    report = generate_insights(df)

    assert report.insight_count == 0


def test_generate_insights_does_not_modify_dataframe():
    df = pd.DataFrame(
        {
            "sales": [10, 20, 30, 100],
            "city": ["Delhi", "Delhi", "Delhi", "Mumbai"],
        }
    )
    original = df.copy(deep=True)

    generate_insights(df)

    pd.testing.assert_frame_equal(df, original)


def test_generate_insights_returns_correct_dimensions():
    df = pd.DataFrame(
        {
            "sales": [10, 20, 30],
            "city": ["Delhi", "Mumbai", "Pune"],
        }
    )

    report = generate_insights(df)

    assert report.row_count == 3
    assert report.column_count == 2


def test_generate_insights_handles_empty_dataframe():
    df = pd.DataFrame()

    report = generate_insights(df)

    assert report.row_count == 0
    assert report.column_count == 0
    assert report.insight_count == 0


def test_generate_insights_rejects_non_dataframe():
    with pytest.raises(TypeError):
        generate_insights([1, 2, 3])
