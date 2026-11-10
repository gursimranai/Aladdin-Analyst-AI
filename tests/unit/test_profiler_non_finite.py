import pandas as pd
import pytest

from aladdin.profiling.profiler import profile_data


def test_numeric_statistics_exclude_infinite_values():
    dataframe = pd.DataFrame({"value": [1.0, 2.0, float("inf"), 4.0, float("-inf")]})

    profile = profile_data(dataframe)
    column = profile.columns[0]

    assert column.non_null_count == 5
    assert column.missing_count == 0

    assert column.mean == pytest.approx(7 / 3)
    assert column.median == pytest.approx(2.0)
    assert column.std == pytest.approx(1.52752523165)
    assert column.min_value == pytest.approx(1.0)
    assert column.max_value == pytest.approx(4.0)


def test_numeric_statistics_are_none_when_all_values_are_infinite():
    dataframe = pd.DataFrame({"value": [float("inf"), float("-inf")]})

    profile = profile_data(dataframe)
    column = profile.columns[0]

    assert column.mean is None
    assert column.median is None
    assert column.std is None
    assert column.min_value is None
    assert column.max_value is None


def test_numeric_statistics_handle_missing_and_infinite_values():
    dataframe = pd.DataFrame({"value": [10.0, None, float("inf"), 20.0, float("-inf")]})

    profile = profile_data(dataframe)
    column = profile.columns[0]

    assert column.non_null_count == 4
    assert column.missing_count == 1
    assert column.mean == pytest.approx(15.0)
    assert column.median == pytest.approx(15.0)
