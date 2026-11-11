import pytest

from aladdin.pipeline.models import AnalysisResult
from aladdin.reporting import (
    ReportConfig,
    ReportFormat,
    export_html_report,
    export_report,
    exporter,
)


def make_analysis_result() -> AnalysisResult:
    """Create a lightweight AnalysisResult for exporter tests."""

    result = AnalysisResult.__new__(AnalysisResult)
    result.source = "sample.csv"
    return result


def test_build_html_document_escapes_untrusted_content():
    report_document = {
        "metadata": {
            "source": "sample.csv",
            "generated_at": "2026-11-11T10:00:00+00:00",
        },
        "profile": {
            "column": "<script>alert('xss')</script>",
        },
    }

    document = exporter._build_html_document(report_document)

    assert "<!DOCTYPE html>" in document
    assert "sample.csv" in document
    assert "&lt;script&gt;" in document
    assert "<script>alert('xss')</script>" not in document


def test_export_html_report_creates_html_file(tmp_path, monkeypatch):
    result = make_analysis_result()

    report_document = {
        "metadata": {
            "source": "sample.csv",
            "generated_at": "2026-11-11T10:00:00+00:00",
            "format": "html",
        },
        "profile": {"rows": 100, "columns": 5},
    }

    monkeypatch.setattr(
        exporter,
        "_build_report_document",
        lambda result, config, generated_at: report_document,
    )

    config = ReportConfig(
        output_dir=tmp_path,
        format=ReportFormat.HTML,
    )

    report = export_html_report(result, config)

    assert report.format == ReportFormat.HTML
    assert report.output_path == tmp_path / "analysis_report.html"
    assert report.output_path.exists()
    assert report.file_size_bytes > 0
    assert report.metadata["source"] == "sample.csv"
    assert report.metadata["sections"] == ["profile"]

    content = report.output_path.read_text(encoding="utf-8")

    assert "<!DOCTYPE html>" in content
    assert "sample.csv" in content
    assert "rows" in content


def test_export_html_report_rejects_wrong_format(tmp_path):
    result = make_analysis_result()

    config = ReportConfig(
        output_dir=tmp_path,
        format=ReportFormat.JSON,
    )

    with pytest.raises(ValueError, match="ReportFormat.HTML"):
        export_html_report(result, config)


def test_export_report_dispatches_html(tmp_path, monkeypatch):
    result = make_analysis_result()
    expected = object()

    def fake_exporter(result, config):
        return expected

    monkeypatch.setattr(exporter, "export_html_report", fake_exporter)

    config = ReportConfig(
        output_dir=tmp_path,
        format=ReportFormat.HTML,
    )

    assert export_report(result, config) is expected


def test_export_report_rejects_unsupported_csv_format(tmp_path):
    result = make_analysis_result()

    config = ReportConfig(
        output_dir=tmp_path,
        format=ReportFormat.CSV,
    )

    with pytest.raises(NotImplementedError, match="CSV"):
        export_report(result, config)
