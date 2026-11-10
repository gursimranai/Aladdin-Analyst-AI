from pathlib import Path

from aladdin import (
    CleaningConfig,
    MissingValueConfig,
    MissingValueStrategy,
    analyze_file,
)


def test_complete_analysis_workflow():
    project_root = Path(__file__).resolve().parents[2]
    file_path = project_root / "datasets" / "sample" / "messy_sales.csv"

    cleaning_config = CleaningConfig(
        missing_values={
            "customer": MissingValueConfig(
                strategy=MissingValueStrategy.FILL_VALUE,
                value="Unknown",
            ),
            "age": MissingValueConfig(
                strategy=MissingValueStrategy.FILL_MEDIAN,
            ),
            "city": MissingValueConfig(
                strategy=MissingValueStrategy.FILL_VALUE,
                value="Unknown",
            ),
            "purchase_amount": MissingValueConfig(
                strategy=MissingValueStrategy.FILL_MEAN,
            ),
        },
        drop_duplicate_rows=True,
        drop_constant_columns=True,
    )

    result = analyze_file(
        file_path,
        cleaning_config=cleaning_config,
    )

    cleaned_data = result.dataframe

    # Verify the initial dataset profile.
    assert result.initial_profile.row_count == 8
    assert result.initial_profile.column_count == 7
    assert result.initial_profile.duplicate_rows == 1

    # Verify the cleaning report.
    cleaning_report = result.cleaning_result.report

    assert cleaning_report.missing_values_filled == 4
    assert cleaning_report.duplicate_rows_removed == 1
    assert cleaning_report.constant_columns_removed == ["source_system"]

    # Verify the final dataset profile.
    assert result.final_profile.row_count == 7
    assert result.final_profile.column_count == 6

    # Verify the source.
    assert result.source == str(file_path)

    # Verify the initial quality assessment.
    assert result.initial_quality_report.has_warnings

    # Verify rows and columns after cleaning.
    assert len(cleaned_data) == 7
    assert len(cleaned_data.columns) == 6

    # Verify missing values were handled.
    assert cleaned_data.isnull().sum().sum() == 0

    # Verify duplicate rows were removed.
    assert not cleaned_data.duplicated().any()

    # Verify the constant column was removed.
    assert "source_system" not in cleaned_data.columns

    # Verify the final quality assessment.
    assert result.final_quality_report.is_healthy
