import csv
import io

import pytest

import aladdin
from aladdin.pipeline.models import AnalysisResult
from aladdin.reporting import (
    ReportConfig,
    ReportFormat,
    export_csv_report,
    export_report,
    exporter,
)


def make_analysis_result() -> AnalysisResult:
    """Create a lightweight AnalysisResult for exporter tests."""

    result = AnalysisResult.__new__(AnalysisResult)
    result.source = "sample.csv"
    return result


def test_flatten_report_value_serializes_fallback_values():
    value = {"coordinates": (10, 20)}

    assert exporter._flatten_report_value(value) == [
        ("coordinates", "[10, 20]", "tuple"),
    ]


def test_flatten_report_value_handles_nested_dictionaries():
    value = {"rows": 100, "profile": {"mean": 25.5}}

    assert exporter._flatten_report_value(value) == [
        ("rows", "100", "int"),
        ("profile.mean", "25.5", "float"),
    ]


def test_flatten_report_value_handles_lists():
    value = {"columns": ["age", "salary"]}

    assert exporter._flatten_report_value(value) == [
        ("columns[0]", "age", "str"),
        ("columns[1]", "salary", "str"),
    ]


def test_flatten_report_value_handles_empty_values():
    value = {
        "missing": None,
        "empty_dict": {},
        "empty_list": [],
        "active": True,
    }

    assert exporter._flatten_report_value(value) == [
        ("missing", "", "null"),
        ("empty_dict", "{}", "dict"),
        ("empty_list", "[]", "list"),
        ("active", "true", "bool"),
    ]


def test_build_csv_document_preserves_sections_and_escaping():
    report_document = {
        "metadata": {"source": "sample.csv"},
        "profile": {
            "description": 'Contains "quoted" values',
            "rows": 100,
        },
    }

    content = exporter._build_csv_document(report_document)
    rows = list(csv.reader(io.StringIO(content)))

    assert rows[0] == ["section", "item", "value", "data_type"]
    assert rows[1] == ["metadata", "source", "sample.csv", "str"]
    assert rows[2] == [
        "profile",
        "description",
        'Contains "quoted" values',
        "str",
    ]


def test_export_csv_report_creates_csv_file(tmp_path, monkeypatch):
    result = make_analysis_result()

    report_document = {
        "metadata": {"source": "sample.csv", "format": "csv"},
        "profile": {"rows": 100, "columns": 5},
    }

    monkeypatch.setattr(
        exporter,
        "_build_report_document",
        lambda result, config, generated_at: report_document,
    )

    config = ReportConfig(output_dir=tmp_path, format=ReportFormat.CSV)
    report = export_csv_report(result, config)

    assert report.format == ReportFormat.CSV
    assert report.output_path == tmp_path / "analysis_report.csv"
    assert report.output_path.exists()
    assert report.file_size_bytes > 0
    assert report.metadata["source"] == "sample.csv"
    assert report.metadata["sections"] == ["profile"]

    with report.output_path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.reader(file))

    assert rows[0] == ["section", "item", "value", "data_type"]
    assert ["profile", "rows", "100", "int"] in rows


def test_export_csv_report_rejects_wrong_format(tmp_path):
    config = ReportConfig(output_dir=tmp_path, format=ReportFormat.JSON)

    with pytest.raises(ValueError, match="ReportFormat.CSV"):
        export_csv_report(make_analysis_result(), config)


def test_export_csv_report_rejects_wrong_extension(tmp_path):
    config = ReportConfig(
        output_dir=tmp_path,
        format=ReportFormat.CSV,
        filename="analysis.json",
    )

    with pytest.raises(ValueError, match=r"\.csv"):
        export_csv_report(make_analysis_result(), config)


def test_export_report_dispatches_csv(tmp_path, monkeypatch):
    expected = object()

    def fake_exporter(result, config):
        return expected

    monkeypatch.setattr(exporter, "export_csv_report", fake_exporter)

    config = ReportConfig(output_dir=tmp_path, format=ReportFormat.CSV)

    assert export_report(make_analysis_result(), config) is expected


def test_csv_exporter_is_available_from_root_package():
    assert aladdin.export_csv_report is export_csv_report


@pytest.mark.parametrize(
    "value",
    [
        "=1+1",
        "+SUM(1,2)",
        "-cmd|' /C calc'!A0",
        "@SUM(A1:A2)",
        "  =1+1",
        "\t=1+1",
    ],
)
def test_build_csv_document_escapes_spreadsheet_formulas(value):
    report_document = {
        "profile": {
            "untrusted": value,
        }
    }

    content = exporter._build_csv_document(report_document)
    rows = list(csv.reader(io.StringIO(content)))

    assert rows[1] == [
        "profile",
        "untrusted",
        f"'{value}",
        "str",
    ]


def test_build_csv_document_preserves_negative_numeric_values():
    report_document = {
        "profile": {
            "temperature": -250,
            "description": "-250",
        }
    }

    content = exporter._build_csv_document(report_document)
    rows = list(csv.reader(io.StringIO(content)))

    assert rows[1] == ["profile", "temperature", "-250", "int"]
    assert rows[2] == ["profile", "description", "'-250", "str"]


def test_flatten_report_value_rejects_unsupported_fallback_value():
    value = {"unsupported": object()}

    with pytest.raises(TypeError):
        exporter._flatten_report_value(value)


def test_export_csv_report_logs_and_reraises_export_error(
    tmp_path,
    monkeypatch,
    caplog,
):
    import logging

    def fail_build(result, config, generated_at):
        raise TypeError("Simulated CSV serialization failure.")

    monkeypatch.setattr(
        exporter,
        "_build_report_document",
        fail_build,
    )

    config = ReportConfig(
        output_dir=tmp_path,
        format=ReportFormat.CSV,
    )

    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            TypeError,
            match="CSV serialization failure",
        ):
            export_csv_report(make_analysis_result(), config)

    assert "Failed to export CSV report" in caplog.text
