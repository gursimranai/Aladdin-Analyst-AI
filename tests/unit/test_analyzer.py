import pandas as pd
import pytest

from aladdin.cleaning.models import (
    CleaningConfig,
    MissingValueConfig,
    MissingValueStrategy,
)
from aladdin.pipeline import analyze_dataframe, analyze_file


def test_analyze_dataframe_returns_complete_result():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob", None],
            "age": [20, 30, 40],
        }
    )

    result = analyze_dataframe(dataframe)

    assert result.initial_profile.row_count == 3
    assert result.initial_quality_report.has_warnings

    assert result.recommendations.row_count == 3
    assert result.recommendations.column_count == 2
    assert result.recommendations.has_recommendations

    assert any(
        recommendation.column_name == "name"
        for recommendation in result.recommendations.recommendations
    )

    assert result.final_profile.row_count == 3
    assert result.final_quality_report.has_warnings

    assert result.dataframe.isna().sum().sum() == 1


def test_analyze_dataframe_with_cleaning_configuration():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob", None],
            "age": [20, 30, 40],
        }
    )

    config = CleaningConfig(
        missing_values={
            "name": MissingValueConfig(
                strategy=MissingValueStrategy.FILL_VALUE,
                value="Unknown",
            )
        }
    )

    result = analyze_dataframe(
        dataframe,
        cleaning_config=config,
    )
    # Recommendations describe the original dataset,
    # even though configured cleaning resolves the issue.
    assert result.recommendations.has_recommendations
    assert any(
        recommendation.column_name == "name"
        for recommendation in result.recommendations.recommendations
    )

    assert result.initial_quality_report.has_warnings
    assert not result.final_quality_report.has_warnings

    assert result.dataframe["name"].isna().sum() == 0
    assert result.cleaning_result.report.missing_values_filled == 1


def test_analyze_dataframe_preserves_original_dataframe():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None, "Charlie"],
            "age": [20, 30, 40],
        }
    )

    original = dataframe.copy(deep=True)

    config = CleaningConfig(
        missing_values={
            "name": MissingValueConfig(
                strategy=MissingValueStrategy.FILL_VALUE,
                value="Unknown",
            )
        }
    )

    analyze_dataframe(dataframe, cleaning_config=config)

    pd.testing.assert_frame_equal(dataframe, original)


def test_analyze_file_loads_and_analyzes_csv(tmp_path):
    file_path = tmp_path / "sample.csv"

    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [20, 30, 40],
        }
    )

    dataframe.to_csv(file_path, index=False)

    result = analyze_file(file_path)

    assert result.source == str(file_path)
    assert result.initial_profile.row_count == 3
    assert result.final_profile.row_count == 3
    assert result.final_quality_report.is_healthy


def test_analyze_file_forwards_loader_arguments(tmp_path):
    file_path = tmp_path / "sample.csv"

    file_path.write_text(
        "name;age\nAlice;20\nBob;30\n",
        encoding="utf-8",
    )

    result = analyze_file(
        file_path,
        sep=";",
    )

    assert result.dataframe.shape == (2, 2)
    assert list(result.dataframe.columns) == ["name", "age"]


def test_analyze_dataframe_rejects_invalid_input():
    with pytest.raises(TypeError, match="pandas DataFrame"):
        analyze_dataframe([1, 2, 3])


def test_analyze_dataframe_includes_insights():
    dataframe = pd.DataFrame(
        {
            "age": [20, None, 30, 40, 50],
            "sales": [10, 12, 11, 13, 200],
        }
    )

    result = analyze_dataframe(dataframe)

    assert result.insights.row_count == 5
    assert result.insights.column_count == 2
    assert result.insights.has_insights

    insight_codes = {item.code for item in result.insights.insights}

    assert "MISSING_VALUES_age" in insight_codes
    assert "POTENTIAL_OUTLIERS_sales" in insight_codes


def test_analyze_dataframe_insights_describe_original_data():
    from aladdin.cleaning.models import (
        CleaningConfig,
        MissingValueConfig,
        MissingValueStrategy,
    )

    dataframe = pd.DataFrame(
        {
            "age": [20, None, 30, 40, 50],
            "sales": [10, 12, 11, 13, 200],
        }
    )

    original = dataframe.copy(deep=True)

    config = CleaningConfig(
        missing_values={
            "age": MissingValueConfig(
                strategy=MissingValueStrategy.DROP_ROWS,
            )
        }
    )

    result = analyze_dataframe(
        dataframe,
        cleaning_config=config,
    )

    insight_codes = {item.code for item in result.insights.insights}

    assert result.initial_profile.row_count == 5
    assert result.final_profile.row_count == 4
    assert "MISSING_VALUES_age" in insight_codes

    pd.testing.assert_frame_equal(dataframe, original)
