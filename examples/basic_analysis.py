from pathlib import Path

from aladdin import analyze_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = PROJECT_ROOT / "datasets" / "sample" / "sample_sales.csv"


def main() -> None:
    """Run a complete analysis on the sample sales dataset."""

    result = analyze_file(DATASET_PATH)

    print("\n" + "=" * 60)
    print("ALADDIN ANALYST AI — DATA ANALYSIS")
    print("=" * 60)

    print(f"\nSource: {result.source}")

    # Initial dataset information
    print("\n[1] INITIAL DATA PROFILE")
    print(f"Rows: {result.initial_profile.row_count}")
    print(f"Columns: {result.initial_profile.column_count}")
    print(f"Duplicate rows: {result.initial_profile.duplicate_rows}")

    # Initial data quality
    print("\n[2] INITIAL DATA QUALITY")
    print(f"Healthy: {result.initial_quality_report.is_healthy}")
    print(f"Issues: {len(result.initial_quality_report.issues)}")

    for issue in result.initial_quality_report.issues:
        print(f"- [{issue.severity}] {issue.message}")

    # Cleaning summary
    print("\n[3] CLEANING SUMMARY")
    report = result.cleaning_result.report

    print(f"Rows: {report.rows_before} -> {report.rows_after}")
    print(f"Columns: {report.columns_before} -> {report.columns_after}")
    print(
        "Missing values: "
        f"{report.missing_values_before} -> "
        f"{report.missing_values_after}"
    )
    print(f"Missing values filled: {report.missing_values_filled}")
    print(f"Duplicate rows removed: {report.duplicate_rows_removed}")

    # Final analysis
    print("\n[4] FINAL DATA QUALITY")
    print(f"Healthy: {result.final_quality_report.is_healthy}")
    print(f"Issues: {len(result.final_quality_report.issues)}")

    print("\n[5] CLEANED DATA PREVIEW")
    print(result.dataframe.head())

    print("\n[6] COLUMN PROFILES")

    for column in result.final_profile.columns:
        print(f"\nColumn: {column.name}")
        print(f"Data type: {column.dtype}")
        print(f"Missing: {column.missing_count}")
        print(f"Unique: {column.unique_count}")

        if column.mean is not None:
            print(f"Mean: {column.mean}")

        if column.median is not None:
            print(f"Median: {column.median}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
