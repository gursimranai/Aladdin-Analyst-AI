from pathlib import Path

from aladdin import (
    CleaningConfig,
    MissingValueConfig,
    MissingValueStrategy,
    analyze_file,
)


def main():
    project_root = Path(__file__).resolve().parents[1]
    dataset_path = project_root / "datasets" / "sample" / "messy_sales.csv"

    config = CleaningConfig(
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

    result = analyze_file(dataset_path, cleaning_config=config)
    report = result.cleaning_result.report

    print("\n" + "=" * 60)
    print("ALADDIN ANALYST AI — REAL-WORLD ANALYSIS")
    print("=" * 60)

    print(f"\nDataset: {result.source}")

    print("\n[1] BEFORE CLEANING")
    print(f"Rows: {result.initial_profile.row_count}")
    print(f"Columns: {result.initial_profile.column_count}")
    print(f"Duplicate rows: {result.initial_profile.duplicate_rows}")
    print(f"Quality healthy: {result.initial_quality_report.is_healthy}")

    print("\n[2] CLEANING SUMMARY")
    print(f"Missing values filled: {report.missing_values_filled}")
    print(f"Duplicate rows removed: {report.duplicate_rows_removed}")
    print(f"Constant columns removed: {report.constant_columns_removed}")

    print("\n[3] AFTER CLEANING")
    print(f"Rows: {result.final_profile.row_count}")
    print(f"Columns: {result.final_profile.column_count}")
    print(f"Quality healthy: {result.final_quality_report.is_healthy}")

    print("\n[4] CLEANED DATA PREVIEW")
    print(result.dataframe.to_string(index=False))

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
