import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from aladdin.visualization.config import VisualizationConfig
from aladdin.visualization.engine import (
    create_bar_chart,
    create_correlation_heatmap,
    create_histogram,
    create_missing_values_chart,
)
from aladdin.visualization.models import ChartType


def test_create_histogram():
    dataframe = pd.DataFrame({"sales": [100, 200, 300, 400, 500]})

    result = create_histogram(dataframe, "sales")

    assert result.chart_type == ChartType.HISTOGRAM
    assert result.title == "Distribution of sales"
    assert result.metadata["column"] == "sales"
    assert result.metadata["observations"] == 5
    assert result.output_path is None

    plt.close(result.figure)


def test_create_histogram_with_custom_options():
    dataframe = pd.DataFrame({"sales": [100, 200, 300]})

    config = VisualizationConfig(width=12, height=8, dpi=150)

    result = create_histogram(
        dataframe,
        "sales",
        config=config,
        bins=10,
        title="Sales Overview",
    )

    assert result.title == "Sales Overview"
    assert result.metadata["bins"] == 10
    assert result.figure.get_size_inches().tolist() == [12.0, 8.0]

    plt.close(result.figure)


def test_create_histogram_saves_file(tmp_path):
    dataframe = pd.DataFrame({"sales": [100, 200, 300]})

    config = VisualizationConfig(
        save=True,
        output_dir=tmp_path,
    )

    result = create_histogram(dataframe, "sales", config=config)

    assert result.output_path.exists()
    assert result.output_path.suffix == ".png"

    plt.close(result.figure)


def test_create_histogram_excludes_non_finite_values():
    dataframe = pd.DataFrame({"sales": [100, 200, np.inf, -np.inf, np.nan]})

    result = create_histogram(dataframe, "sales")

    assert result.metadata["observations"] == 2
    assert result.metadata["excluded_non_finite"] == 2

    plt.close(result.figure)


def test_create_histogram_rejects_non_dataframe():
    with pytest.raises(TypeError):
        create_histogram([1, 2, 3], "sales")


def test_create_histogram_rejects_missing_column():
    dataframe = pd.DataFrame({"sales": [100, 200]})

    with pytest.raises(ValueError, match="does not exist"):
        create_histogram(dataframe, "revenue")


def test_create_histogram_rejects_non_numeric_column():
    dataframe = pd.DataFrame({"customer": ["A", "B", "C"]})

    with pytest.raises(TypeError, match="numerical data"):
        create_histogram(dataframe, "customer")


def test_create_histogram_rejects_invalid_bins():
    dataframe = pd.DataFrame({"sales": [100, 200, 300]})

    with pytest.raises(ValueError):
        create_histogram(dataframe, "sales", bins=0)


def test_create_histogram_rejects_empty_finite_values():
    dataframe = pd.DataFrame({"sales": [np.inf, -np.inf, np.nan]})

    with pytest.raises(ValueError, match="no finite"):
        create_histogram(dataframe, "sales")


def test_create_histogram_does_not_modify_dataframe():
    dataframe = pd.DataFrame({"sales": [100, 200, 300]})
    original = dataframe.copy(deep=True)

    result = create_histogram(dataframe, "sales")

    pd.testing.assert_frame_equal(dataframe, original)

    plt.close(result.figure)


def test_create_bar_chart():
    dataframe = pd.DataFrame(
        {"city": ["Delhi", "Mumbai", "Delhi", "Chandigarh", "Mumbai"]}
    )

    result = create_bar_chart(dataframe, "city")

    frequencies = result.metadata["frequencies"]

    assert result.chart_type == ChartType.BAR
    assert result.metadata["observations"] == 5
    assert result.metadata["categories"] == 3

    delhi = next(item for item in frequencies if item["category"] == "Delhi")
    mumbai = next(item for item in frequencies if item["category"] == "Mumbai")

    assert delhi["count"] == 2
    assert mumbai["count"] == 2


def test_create_bar_chart_with_top_n():
    dataframe = pd.DataFrame({"city": ["Delhi"] * 5 + ["Mumbai"] * 3 + ["Pune"] * 2})

    result = create_bar_chart(dataframe, "city", top_n=2)

    frequencies = result.metadata["frequencies"]

    assert result.metadata["categories"] == 3

    other = next(item for item in frequencies if item["kind"] == "other")

    assert other["count"] == 2


def test_create_bar_chart_includes_missing_values():
    dataframe = pd.DataFrame({"city": ["Delhi", None, "Mumbai", None]})

    result = create_bar_chart(dataframe, "city")

    frequencies = result.metadata["frequencies"]

    missing = next(item for item in frequencies if item["kind"] == "missing")

    assert missing["count"] == 2
    assert result.metadata["observations"] == 4


def test_create_bar_chart_excludes_missing_values():
    dataframe = pd.DataFrame({"city": ["Delhi", None, "Mumbai"]})

    result = create_bar_chart(
        dataframe,
        "city",
        include_missing=False,
    )

    assert result.metadata["observations"] == 2

    plt.close(result.figure)


def test_create_bar_chart_saves_file(tmp_path):
    dataframe = pd.DataFrame({"city": ["Delhi", "Mumbai", "Delhi"]})

    config = VisualizationConfig(
        save=True,
        output_dir=tmp_path,
    )

    result = create_bar_chart(dataframe, "city", config=config)

    assert result.output_path.exists()
    assert result.output_path.suffix == ".png"

    plt.close(result.figure)


def test_create_bar_chart_rejects_non_categorical_column():
    dataframe = pd.DataFrame({"sales": [100, 200, 300]})

    with pytest.raises(TypeError, match="categorical data"):
        create_bar_chart(dataframe, "sales")


def test_create_bar_chart_rejects_empty_values():
    dataframe = pd.DataFrame({"city": [None, None]})

    with pytest.raises(ValueError, match="no categorical values"):
        create_bar_chart(dataframe, "city", include_missing=False)


def test_create_bar_chart_rejects_invalid_top_n():
    dataframe = pd.DataFrame({"city": ["Delhi", "Mumbai"]})

    with pytest.raises(ValueError):
        create_bar_chart(dataframe, "city", top_n=0)


def test_create_bar_chart_does_not_modify_dataframe():
    dataframe = pd.DataFrame({"city": ["Delhi", None, "Mumbai"]})
    original = dataframe.copy(deep=True)

    result = create_bar_chart(dataframe, "city")

    pd.testing.assert_frame_equal(dataframe, original)

    plt.close(result.figure)


def test_create_bar_chart_preserves_real_missing_category():
    dataframe = pd.DataFrame({"category": ["Missing", "A", None, "A"]})

    result = create_bar_chart(dataframe, "category", top_n=None)

    frequencies = result.metadata["frequencies"]

    assert result.metadata["observations"] == 4
    assert len(frequencies) == 3

    real_missing = next(
        item
        for item in frequencies
        if item["kind"] == "category" and item["category"] == "Missing"
    )

    generated_missing = next(item for item in frequencies if item["kind"] == "missing")

    assert real_missing["count"] == 1
    assert generated_missing["count"] == 1
    assert real_missing["label"] != generated_missing["label"]


def test_create_bar_chart_preserves_real_other_category():
    dataframe = pd.DataFrame(
        {
            "category": [
                "Other",
                "Other",
                "Other",
                "A",
                "A",
                "B",
                "B",
                "C",
            ]
        }
    )

    result = create_bar_chart(
        dataframe,
        "category",
        top_n=2,
    )

    frequencies = result.metadata["frequencies"]

    real_other = next(
        item
        for item in frequencies
        if item["kind"] == "category" and item["category"] == "Other"
    )

    generated_other = next(item for item in frequencies if item["kind"] == "other")

    assert real_other["count"] == 3
    assert generated_other["count"] == 3
    assert real_other["label"] != generated_other["label"]


def test_create_bar_chart_preserves_distinct_string_representations():
    dataframe = pd.DataFrame({"category": pd.Series([1, "1", 1, "1"], dtype="object")})

    result = create_bar_chart(
        dataframe,
        "category",
        top_n=None,
    )

    frequencies = result.metadata["frequencies"]

    assert len(frequencies) == 2
    assert {item["kind"] for item in frequencies} == {"category"}

    assert {(type(item["category"]), item["count"]) for item in frequencies} == {
        (int, 2),
        (str, 2),
    }


def test_create_bar_chart_preserves_aggregated_category_metadata():
    dataframe = pd.DataFrame({"category": ["A", "A", "B", "C", "D"]})

    result = create_bar_chart(
        dataframe,
        "category",
        top_n=2,
    )

    assert set(result.metadata["aggregated_categories"]) == {"C", "D"}

    generated_other = next(
        item for item in result.metadata["frequencies"] if item["kind"] == "other"
    )

    assert generated_other["count"] == 2


def test_create_missing_values_chart():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None, "Charlie", None],
            "age": [20, 21, None, 23],
            "city": ["Delhi", "Mumbai", "Pune", "Chandigarh"],
        }
    )

    result = create_missing_values_chart(dataframe)

    assert result.chart_type == ChartType.MISSING_VALUES
    assert result.metadata["columns_analyzed"] == 3
    assert result.metadata["columns_displayed"] == 2
    assert result.metadata["total_missing_values"] == 3

    counts = {
        item["column"]: item["missing_count"]
        for item in result.metadata["missing_counts"]
    }

    assert counts == {"name": 2, "age": 1}


def test_create_missing_values_chart_includes_zero_counts():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None],
            "age": [20, 21],
            "city": ["Delhi", "Mumbai"],
        }
    )

    result = create_missing_values_chart(
        dataframe,
        include_zero_missing=True,
    )

    assert result.metadata["columns_displayed"] == 3

    counts = {
        item["column"]: item["missing_count"]
        for item in result.metadata["missing_counts"]
    }

    assert counts == {"name": 1, "age": 0, "city": 0}


def test_create_missing_values_chart_custom_title():
    dataframe = pd.DataFrame({"age": [20, None]})

    result = create_missing_values_chart(
        dataframe,
        title="Dataset Missingness",
    )

    assert result.title == "Dataset Missingness"


def test_create_missing_values_chart_saves_file(tmp_path):
    dataframe = pd.DataFrame({"age": [20, None]})

    config = VisualizationConfig(
        save=True,
        output_dir=tmp_path,
    )

    result = create_missing_values_chart(dataframe, config=config)

    assert result.output_path.exists()
    assert result.output_path.suffix == ".png"


def test_create_missing_values_chart_rejects_non_dataframe():
    with pytest.raises(TypeError):
        create_missing_values_chart([1, 2, 3])


def test_create_missing_values_chart_rejects_empty_columns():
    dataframe = pd.DataFrame()

    with pytest.raises(ValueError, match="at least one column"):
        create_missing_values_chart(dataframe)


def test_create_missing_values_chart_rejects_duplicate_columns():
    dataframe = pd.DataFrame(
        [[1, None]],
        columns=["age", "age"],
    )

    with pytest.raises(ValueError, match="duplicate column labels"):
        create_missing_values_chart(dataframe)


def test_create_missing_values_chart_rejects_no_missing_values():
    dataframe = pd.DataFrame({"age": [20, 21], "city": ["Delhi", "Mumbai"]})

    with pytest.raises(ValueError, match="No missing values"):
        create_missing_values_chart(dataframe)


def test_create_missing_values_chart_rejects_invalid_option():
    dataframe = pd.DataFrame({"age": [20, None]})

    with pytest.raises(TypeError, match="include_zero_missing"):
        create_missing_values_chart(
            dataframe,
            include_zero_missing="yes",
        )


def test_create_missing_values_chart_does_not_modify_dataframe():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None],
            "age": [20, None],
        }
    )

    original = dataframe.copy(deep=True)

    create_missing_values_chart(dataframe)

    pd.testing.assert_frame_equal(dataframe, original)


def test_create_correlation_heatmap():
    dataframe = pd.DataFrame(
        {
            "sales": [10, 20, 30, 40, 50],
            "profit": [20, 40, 60, 80, 100],
            "customers": [50, 40, 30, 20, 10],
            "city": ["A", "B", "A", "B", "A"],
        }
    )

    result = create_correlation_heatmap(dataframe)

    assert result.chart_type == ChartType.CORRELATION_HEATMAP
    assert result.metadata["method"] == "pearson"
    assert result.metadata["column_count"] == 3

    matrix = result.metadata["correlation_matrix"]

    assert matrix["sales"]["profit"] == pytest.approx(1.0)
    assert matrix["sales"]["customers"] == pytest.approx(-1.0)


def test_create_correlation_heatmap_excludes_boolean_columns():
    dataframe = pd.DataFrame(
        {
            "sales": [10, 20, 30, 40],
            "profit": [20, 40, 60, 80],
            "active": [True, False, True, False],
        }
    )

    result = create_correlation_heatmap(dataframe)

    assert result.metadata["columns"] == ["sales", "profit"]


def test_create_correlation_heatmap_excludes_constant_columns():
    dataframe = pd.DataFrame(
        {
            "sales": [10, 20, 30, 40],
            "profit": [20, 40, 60, 80],
            "constant": [5, 5, 5, 5],
        }
    )

    result = create_correlation_heatmap(dataframe)

    assert result.metadata["columns"] == ["sales", "profit"]


def test_create_correlation_heatmap_handles_infinity():
    dataframe = pd.DataFrame(
        {
            "sales": [10, 20, np.inf, 40, 50],
            "profit": [20, 40, 60, 80, 100],
        }
    )

    result = create_correlation_heatmap(dataframe)

    assert result.metadata["column_count"] == 2

    correlation = result.metadata["correlation_matrix"]["sales"]["profit"]

    assert correlation is not None
    assert np.isfinite(correlation)


def test_create_correlation_heatmap_uses_pairwise_observations():
    dataframe = pd.DataFrame(
        {
            "sales": [10, 20, 30, None, 50],
            "profit": [20, 40, None, 80, 100],
        }
    )

    result = create_correlation_heatmap(dataframe)

    correlation = result.metadata["correlation_matrix"]["sales"]["profit"]

    assert correlation == pytest.approx(1.0)


def test_create_correlation_heatmap_rejects_non_dataframe():
    with pytest.raises(TypeError):
        create_correlation_heatmap([1, 2, 3])


def test_create_correlation_heatmap_rejects_insufficient_numeric_columns():
    dataframe = pd.DataFrame(
        {
            "sales": [10, 20, 30],
            "city": ["A", "B", "C"],
        }
    )

    with pytest.raises(ValueError, match="At least two numerical columns"):
        create_correlation_heatmap(dataframe)


def test_create_correlation_heatmap_rejects_constant_numeric_columns():
    dataframe = pd.DataFrame(
        {
            "sales": [10, 10, 10],
            "profit": [20, 20, 20],
        }
    )

    with pytest.raises(ValueError, match="non-constant"):
        create_correlation_heatmap(dataframe)


def test_create_correlation_heatmap_saves_file(tmp_path):
    dataframe = pd.DataFrame(
        {
            "sales": [10, 20, 30, 40],
            "profit": [20, 40, 60, 80],
        }
    )

    config = VisualizationConfig(
        save=True,
        output_dir=tmp_path,
    )

    result = create_correlation_heatmap(dataframe, config=config)

    assert result.output_path.exists()
    assert result.output_path.suffix == ".png"


def test_create_correlation_heatmap_does_not_modify_dataframe():
    dataframe = pd.DataFrame(
        {
            "sales": [10, 20, np.inf, 40],
            "profit": [20, 40, 60, 80],
        }
    )

    original = dataframe.copy(deep=True)

    create_correlation_heatmap(dataframe)

    pd.testing.assert_frame_equal(dataframe, original)
