import pandas as pd
import pytest

from aladdin.cleaning import (
    CleaningConfig,
    MissingValueConfig,
    MissingValueStrategy,
    clean_data,
)


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob", None, "David"],
            "age": [22, 25, None, 30],
            "city": ["Delhi", "Mumbai", "Delhi", "Chandigarh"],
        }
    )


def test_clean_data_without_configuration(sample_dataframe):
    result = clean_data(sample_dataframe)

    pd.testing.assert_frame_equal(
        result.dataframe,
        sample_dataframe,
    )

    assert result.report.missing_values_filled == 0


def test_fill_missing_values_with_explicit_value():
    dataframe = pd.DataFrame({"city": ["Delhi", None, "Mumbai"]})

    config = CleaningConfig(
        missing_values={
            "city": MissingValueConfig(
                strategy=MissingValueStrategy.FILL_VALUE,
                value="Unknown",
            )
        }
    )

    result = clean_data(dataframe, config)

    assert result.dataframe["city"].isna().sum() == 0
    assert result.dataframe.loc[1, "city"] == "Unknown"
    assert result.report.missing_values_filled == 1


def test_fill_missing_values_with_mean():
    dataframe = pd.DataFrame({"age": [20, 30, None, 40]})

    config = CleaningConfig(
        missing_values={
            "age": MissingValueConfig(strategy=MissingValueStrategy.FILL_MEAN)
        }
    )

    result = clean_data(dataframe, config)

    assert result.dataframe.loc[2, "age"] == 30.0
    assert result.report.missing_values_filled == 1


def test_fill_missing_values_with_median():
    dataframe = pd.DataFrame({"age": [20, 30, None, 100]})

    config = CleaningConfig(
        missing_values={
            "age": MissingValueConfig(strategy=MissingValueStrategy.FILL_MEDIAN)
        }
    )

    result = clean_data(dataframe, config)

    assert result.dataframe.loc[2, "age"] == 30.0


def test_fill_missing_values_with_mode():
    dataframe = pd.DataFrame({"city": ["Delhi", "Mumbai", "Delhi", None]})

    config = CleaningConfig(
        missing_values={
            "city": MissingValueConfig(strategy=MissingValueStrategy.FILL_MODE)
        }
    )

    result = clean_data(dataframe, config)

    assert result.dataframe.loc[3, "city"] == "Delhi"


def test_keep_missing_values():
    dataframe = pd.DataFrame({"value": [10, None, 30]})

    config = CleaningConfig(
        missing_values={"value": MissingValueConfig(strategy=MissingValueStrategy.KEEP)}
    )

    result = clean_data(dataframe, config)

    assert result.dataframe["value"].isna().sum() == 1


def test_drop_rows_with_missing_values():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None, "Charlie"],
            "age": [22, 25, 30],
        }
    )

    config = CleaningConfig(
        missing_values={
            "name": MissingValueConfig(strategy=MissingValueStrategy.DROP_ROWS)
        }
    )

    result = clean_data(dataframe, config)

    assert len(result.dataframe) == 2
    assert result.report.rows_removed_for_missing_values == 1


def test_remove_duplicate_rows():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Alice"],
            "age": [22, 25, 22],
        }
    )

    config = CleaningConfig(drop_duplicate_rows=True)

    result = clean_data(dataframe, config)

    assert len(result.dataframe) == 2
    assert result.report.duplicate_rows_removed == 1


def test_remove_constant_columns():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "country": ["India", "India", "India"],
        }
    )

    config = CleaningConfig(drop_constant_columns=True)

    result = clean_data(dataframe, config)

    assert list(result.dataframe.columns) == ["name"]
    assert result.report.constant_columns_removed == ["country"]


def test_all_missing_column_is_not_removed_as_constant():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob"],
            "unused": [None, None],
        }
    )

    config = CleaningConfig(drop_constant_columns=True)

    result = clean_data(dataframe, config)

    assert "unused" in result.dataframe.columns


def test_multiple_cleaning_operations():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Bob", None],
            "age": [20, 30, 30, 40],
            "country": ["India", "India", "India", "India"],
        }
    )

    config = CleaningConfig(
        missing_values={
            "name": MissingValueConfig(
                strategy=MissingValueStrategy.FILL_VALUE,
                value="Unknown",
            )
        },
        drop_duplicate_rows=True,
        drop_constant_columns=True,
    )

    result = clean_data(dataframe, config)

    assert result.dataframe["name"].isna().sum() == 0
    assert len(result.dataframe) == 3
    assert "country" not in result.dataframe.columns


def test_original_dataframe_is_not_modified(sample_dataframe):
    original = sample_dataframe.copy(deep=True)

    config = CleaningConfig(
        missing_values={
            "age": MissingValueConfig(strategy=MissingValueStrategy.FILL_MEAN)
        },
        drop_duplicate_rows=True,
        drop_constant_columns=True,
    )

    clean_data(sample_dataframe, config)

    pd.testing.assert_frame_equal(
        sample_dataframe,
        original,
    )


def test_unknown_column_raises_error():
    dataframe = pd.DataFrame({"age": [20, None]})

    config = CleaningConfig(
        missing_values={
            "salary": MissingValueConfig(strategy=MissingValueStrategy.FILL_MEAN)
        }
    )

    with pytest.raises(ValueError, match="does not exist"):
        clean_data(dataframe, config)


def test_mean_strategy_rejects_non_numeric_column():
    dataframe = pd.DataFrame({"city": ["Delhi", None, "Mumbai"]})

    config = CleaningConfig(
        missing_values={
            "city": MissingValueConfig(strategy=MissingValueStrategy.FILL_MEAN)
        }
    )

    with pytest.raises(TypeError, match="numeric column"):
        clean_data(dataframe, config)


def test_cleaning_report_counts_changes():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Bob"],
            "age": [20, None, None],
        }
    )

    config = CleaningConfig(
        missing_values={
            "age": MissingValueConfig(
                strategy=MissingValueStrategy.FILL_VALUE,
                value=0,
            )
        },
        drop_duplicate_rows=True,
    )

    result = clean_data(dataframe, config)

    assert result.report.rows_before == 3
    assert result.report.rows_after == 2
    assert result.report.missing_values_before == 2
    assert result.report.missing_values_after == 0
    assert result.report.missing_values_filled == 2
    assert result.report.duplicate_rows_removed == 1
