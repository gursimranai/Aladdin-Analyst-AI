from datetime import datetime
from pathlib import Path

import pytest

from aladdin.reporting.models import ReportConfig, ReportFormat, ReportResult


def test_report_config_defaults(tmp_path):
    config = ReportConfig(output_dir=tmp_path)

    assert config.format == ReportFormat.JSON
    assert config.filename is None
    assert config.include_profile is True
    assert config.include_quality is True
    assert config.include_recommendations is True
    assert config.include_insights is True
    assert config.include_cleaning_summary is True


def test_report_config_converts_output_dir_to_path(tmp_path):
    config = ReportConfig(output_dir=str(tmp_path))

    assert isinstance(config.output_dir, Path)
    assert config.output_dir == tmp_path


def test_report_config_accepts_custom_settings(tmp_path):
    config = ReportConfig(
        output_dir=tmp_path,
        format=ReportFormat.HTML,
        filename="analysis_report",
        include_profile=False,
        include_quality=True,
        include_insights=False,
    )

    assert config.format == ReportFormat.HTML
    assert config.filename == "analysis_report"
    assert config.include_profile is False
    assert config.include_quality is True
    assert config.include_insights is False


def test_report_config_rejects_invalid_output_dir():
    with pytest.raises(TypeError):
        ReportConfig(output_dir=123)


def test_report_config_rejects_invalid_format(tmp_path):
    with pytest.raises(TypeError):
        ReportConfig(output_dir=tmp_path, format="json")


@pytest.mark.parametrize("filename", ["", "   "])
def test_report_config_rejects_empty_filename(tmp_path, filename):
    with pytest.raises(ValueError):
        ReportConfig(output_dir=tmp_path, filename=filename)


def test_report_config_rejects_directory_in_filename(tmp_path):
    with pytest.raises(ValueError):
        ReportConfig(output_dir=tmp_path, filename="../report.json")


def test_report_config_rejects_non_string_filename(tmp_path):
    with pytest.raises(TypeError):
        ReportConfig(output_dir=tmp_path, filename=123)


@pytest.mark.parametrize(
    "field_name",
    [
        "include_profile",
        "include_quality",
        "include_recommendations",
        "include_insights",
        "include_cleaning_summary",
    ],
)
def test_report_config_rejects_non_boolean_options(tmp_path, field_name):
    with pytest.raises(TypeError):
        ReportConfig(output_dir=tmp_path, **{field_name: "yes"})


def test_report_result_valid_creation(tmp_path):
    result = ReportResult(
        format=ReportFormat.JSON,
        output_path=tmp_path / "report.json",
        file_size_bytes=1024,
    )

    assert result.format == ReportFormat.JSON
    assert result.output_path == tmp_path / "report.json"
    assert result.file_size_bytes == 1024
    assert isinstance(result.generated_at, datetime)
    assert result.metadata == {}


def test_report_result_converts_output_path_to_path():
    result = ReportResult(
        format=ReportFormat.HTML,
        output_path="report.html",
        file_size_bytes=500,
    )

    assert isinstance(result.output_path, Path)
    assert result.output_path == Path("report.html")


def test_report_result_accepts_custom_metadata(tmp_path):
    metadata = {"rows": 100, "columns": 5}

    result = ReportResult(
        format=ReportFormat.CSV,
        output_path=tmp_path / "data.csv",
        file_size_bytes=2048,
        metadata=metadata,
    )

    assert result.metadata == metadata


def test_report_result_uses_independent_metadata_defaults(tmp_path):
    first = ReportResult(ReportFormat.JSON, tmp_path / "first.json", 100)
    second = ReportResult(ReportFormat.JSON, tmp_path / "second.json", 200)

    first.metadata["rows"] = 10

    assert second.metadata == {}


def test_report_result_rejects_invalid_format(tmp_path):
    with pytest.raises(TypeError):
        ReportResult("json", tmp_path / "report.json", 100)


def test_report_result_rejects_invalid_output_path():
    with pytest.raises(TypeError):
        ReportResult(ReportFormat.JSON, 123, 100)


@pytest.mark.parametrize("size", [-1, 1.5, True, "100"])
def test_report_result_rejects_invalid_file_size(tmp_path, size):
    with pytest.raises(ValueError):
        ReportResult(
            ReportFormat.JSON,
            tmp_path / "report.json",
            size,
        )


def test_report_result_rejects_invalid_generated_at(tmp_path):
    with pytest.raises(TypeError):
        ReportResult(
            ReportFormat.JSON,
            tmp_path / "report.json",
            100,
            generated_at="2026-11-10",
        )


def test_report_result_rejects_invalid_metadata(tmp_path):
    with pytest.raises(TypeError):
        ReportResult(
            ReportFormat.JSON,
            tmp_path / "report.json",
            100,
            metadata=["invalid"],
        )


@pytest.mark.parametrize(
    "filename",
    [
        "../report.json",
        "..\\report.json",
        "reports/report.json",
        "reports\\report.json",
        "C:\\reports\\report.json",
        "/reports/report.json",
        ".",
        "..",
    ],
)
def test_report_config_rejects_path_traversal(tmp_path, filename):
    with pytest.raises(ValueError, match="directory paths"):
        ReportConfig(output_dir=tmp_path, filename=filename)
