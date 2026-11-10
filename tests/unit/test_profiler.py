import pandas as pd
import pytest

from aladdin.profiling import profile_data


@pytest.fixture
def sample_dataframe():
    """Create a sample dataset for profiling tests."""

    return pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard", "Laptop"],
            "price": [75000, 1200, 2500, 75000],
            "quantity": [2, 5, 3, 2],
        }
    )


def test_profile_data_returns_data_profile(sample_dataframe):
    """Test that profiling returns a structured result."""

    profile = profile_data(sample_dataframe)

    assert profile.row_count == 4
    assert profile.column_count == 3


def test_profile_data_counts_duplicate_rows(sample_dataframe):
    """Test duplicate row detection."""

    profile = profile_data(sample_dataframe)

    assert profile.duplicate_rows == 1


def test_profile_data_column_names(sample_dataframe):
    """Test column name extraction."""

    profile = profile_data(sample_dataframe)

    assert [column.name for column in profile.columns] == [
        "product",
        "price",
        "quantity",
    ]


def test_profile_data_missing_values():
    """Test missing value calculations."""

    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None, "Charlie", None],
        }
    )

    profile = profile_data(dataframe)

    column = profile.columns[0]

    assert column.missing_count == 2
    assert column.missing_percentage == 50.0
    assert column.non_null_count == 2


def test_profile_data_unique_values():
    """Test unique value calculations."""

    dataframe = pd.DataFrame(
        {
            "category": ["A", "B", "A", "C", None],
        }
    )

    profile = profile_data(dataframe)

    column = profile.columns[0]

    assert column.unique_count == 3
    assert column.unique_percentage == 75.0


def test_profile_data_numerical_statistics(sample_dataframe):
    """Test numerical descriptive statistics."""

    profile = profile_data(sample_dataframe)

    price_column = profile.columns[1]

    assert price_column.mean == 38425.0
    assert price_column.median == 38750.0
    assert price_column.min_value == 1200.0
    assert price_column.max_value == 75000.0


def test_profile_data_categorical_top_values(sample_dataframe):
    """Test most frequent categorical values."""

    profile = profile_data(sample_dataframe)

    product_column = profile.columns[0]

    assert product_column.top_values[0] == ("Laptop", 2)


def test_profile_data_custom_top_n():
    """Test configurable number of frequent categorical values."""

    dataframe = pd.DataFrame(
        {
            "category": ["A", "A", "B", "B", "C", "D"],
        }
    )

    profile = profile_data(dataframe, top_n=2)

    assert len(profile.columns[0].top_values) == 2


def test_profile_data_empty_dataframe():
    """Test profiling an empty DataFrame."""

    dataframe = pd.DataFrame()

    profile = profile_data(dataframe)

    assert profile.row_count == 0
    assert profile.column_count == 0
    assert profile.duplicate_rows == 0
    assert profile.columns == []


def test_profile_data_empty_rows_with_columns():
    """Test profiling a DataFrame with columns but no rows."""

    dataframe = pd.DataFrame(
        {
            "name": pd.Series(dtype="object"),
            "price": pd.Series(dtype="float64"),
        }
    )

    profile = profile_data(dataframe)

    assert profile.row_count == 0
    assert profile.column_count == 2
    assert profile.columns[0].missing_percentage == 0.0
    assert profile.columns[1].mean is None


def test_profile_data_invalid_input():
    """Test invalid input handling."""

    with pytest.raises(TypeError):
        profile_data([1, 2, 3])


def test_profile_data_invalid_top_n():
    """Test invalid top_n handling."""

    dataframe = pd.DataFrame({"value": ["A", "B"]})

    with pytest.raises(ValueError):
        profile_data(dataframe, top_n=0)


def test_profile_data_non_integer_top_n():
    """Test non-integer top_n handling."""

    dataframe = pd.DataFrame({"value": ["A", "B"]})

    with pytest.raises(TypeError):
        profile_data(dataframe, top_n=2.5)
