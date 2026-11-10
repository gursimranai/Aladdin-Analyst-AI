import pytest

from aladdin.cleaning.models import (
    CleaningConfig,
    MissingValueConfig,
    MissingValueStrategy,
)


def test_default_missing_value_config():
    config = MissingValueConfig()

    assert config.strategy == MissingValueStrategy.KEEP
    assert config.value is None


def test_missing_value_config_with_fill_value():
    config = MissingValueConfig(
        strategy=MissingValueStrategy.FILL_VALUE,
        value="Unknown",
    )

    assert config.strategy == MissingValueStrategy.FILL_VALUE
    assert config.value == "Unknown"


def test_fill_value_requires_non_none_value():
    with pytest.raises(ValueError):
        MissingValueConfig(
            strategy=MissingValueStrategy.FILL_VALUE,
        )


def test_invalid_missing_value_strategy():
    with pytest.raises(TypeError):
        MissingValueConfig(strategy="fill_mean")


def test_default_cleaning_config():
    config = CleaningConfig()

    assert config.missing_values == {}
    assert config.drop_duplicate_rows is False
    assert config.drop_constant_columns is False


def test_custom_cleaning_config():
    config = CleaningConfig(
        missing_values={
            "age": MissingValueConfig(strategy=MissingValueStrategy.FILL_MEDIAN)
        },
        drop_duplicate_rows=True,
        drop_constant_columns=True,
    )

    assert "age" in config.missing_values
    assert config.drop_duplicate_rows is True
    assert config.drop_constant_columns is True


def test_invalid_missing_values_type():
    with pytest.raises(TypeError):
        CleaningConfig(missing_values=[])


def test_invalid_missing_value_config_entry():
    with pytest.raises(TypeError):
        CleaningConfig(missing_values={"age": "fill_median"})


def test_invalid_drop_duplicate_rows_type():
    with pytest.raises(TypeError):
        CleaningConfig(drop_duplicate_rows=1)


def test_invalid_drop_constant_columns_type():
    with pytest.raises(TypeError):
        CleaningConfig(drop_constant_columns="yes")
