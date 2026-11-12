import csv
import json
from pathlib import Path

from aladdin import (
    CleaningConfig,
    MissingValueConfig,
    MissingValueStrategy,
    ReportConfig,
    ReportFormat,
    ReportResult,
    analyze_file,
    export_report,
)


def test_complete_analysis_workflow(tmp_path: Path):
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

    # Verify JSON, HTML, and CSV report exports through the public API.
    report_dir = tmp_path / "reports"

    expected_sections = {
        "profile",
        "quality",
        "recommendations",
        "insights",
        "cleaning_summary",
    }

    for report_format in (
        ReportFormat.JSON,
        ReportFormat.HTML,
        ReportFormat.CSV,
    ):
        report_result = export_report(
            result,
            ReportConfig(
                output_dir=report_dir / report_format.value,
                format=report_format,
            ),
        )

        assert isinstance(report_result, ReportResult)
        assert report_result.format == report_format
        assert report_result.output_path.exists()
        assert report_result.output_path.stat().st_size > 0
        assert report_result.file_size_bytes == report_result.output_path.stat().st_size
        assert report_result.metadata["source"] == str(file_path)

        if report_format == ReportFormat.JSON:
            report_document = json.loads(
                report_result.output_path.read_text(encoding="utf-8")
            )

            assert expected_sections.issubset(report_document.keys())
            assert report_document["metadata"]["format"] == "json"
            assert report_document["metadata"]["source"] == str(file_path)

        elif report_format == ReportFormat.HTML:
            html_document = report_result.output_path.read_text(encoding="utf-8")

            assert "<html" in html_document.lower()
            assert "</html>" in html_document.lower()

        elif report_format == ReportFormat.CSV:
            with report_result.output_path.open(
                "r",
                encoding="utf-8",
                newline="",
            ) as csv_file:
                csv_rows = list(csv.DictReader(csv_file))

            assert csv_rows
            assert {
                "section",
                "item",
                "value",
                "data_type",
            }.issubset(csv_rows[0].keys())

            exported_sections = {row["section"] for row in csv_rows}

            assert expected_sections.issubset(exported_sections)
