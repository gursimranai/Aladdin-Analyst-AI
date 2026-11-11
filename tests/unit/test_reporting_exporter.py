import json
from datetime import date, datetime, time
from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from aladdin.cleaning.models import CleaningReport, CleaningResult
from aladdin.insights.models import InsightReport
from aladdin.pipeline.models import AnalysisResult
from aladdin.profiling.models import ColumnProfile, DataProfile
from aladdin.quality.models import DataQualityReport
from aladdin.recommendations.models import RecommendationReport
from aladdin.reporting.exporter import _to_json_safe, export_json_report
from aladdin.reporting.models import ReportConfig, ReportFormat, ReportResult


@pytest.fixture
def analysis_result():
    initial_profile = DataProfile(
        row_count=4,
        column_count=1,
        duplicate_rows=0,
        columns=[
            ColumnProfile(
                name="revenue",
                dtype="float64",
                non_null_count=3,
                missing_count=1,
                missing_percentage=25.0,
                unique_count=3,
                unique_percentage=75.0,
                mean=float("nan"),
                top_values=[(np.int64(100), np.int64(2))],
            )
        ],
    )

    final_profile = DataProfile(
        row_count=3,
        column_count=1,
        duplicate_rows=0,
        columns=[
            ColumnProfile(
                name="revenue",
                dtype="int64",
                non_null_count=3,
                missing_count=0,
                missing_percentage=0.0,
                unique_count=3,
                unique_percentage=100.0,
                mean=200.0,
            )
        ],
    )

    dataframe = pd.DataFrame({"revenue": [100, 200, 300]})

    cleaning_report = CleaningReport(
        rows_before=4,
        rows_after=3,
        columns_before=1,
        columns_after=1,
        missing_values_before=1,
        missing_values_after=0,
        missing_values_filled=1,
    )

    return AnalysisResult(
        initial_profile=initial_profile,
        initial_quality_report=DataQualityReport(4, 1),
        recommendations=RecommendationReport(4, 1),
        insights=InsightReport(4, 1),
        cleaning_result=CleaningResult(dataframe, cleaning_report),
        final_profile=final_profile,
        final_quality_report=DataQualityReport(3, 1),
        source="sample_sales.csv",
    )


def test_export_json_report_creates_valid_json(tmp_path, analysis_result):
    config = ReportConfig(output_dir=tmp_path)

    result = export_json_report(analysis_result, config)

    assert isinstance(result, ReportResult)
    assert result.format == ReportFormat.JSON
    assert result.output_path.exists()
    assert result.output_path.suffix == ".json"

    document = json.loads(result.output_path.read_text(encoding="utf-8"))

    assert document["metadata"]["source"] == "sample_sales.csv"
    assert "profile" in document
    assert "quality" in document
    assert "recommendations" in document
    assert "insights" in document
    assert "cleaning_summary" in document


def test_export_json_report_returns_correct_file_size(tmp_path, analysis_result):
    result = export_json_report(
        analysis_result,
        ReportConfig(output_dir=tmp_path),
    )

    assert result.file_size_bytes == result.output_path.stat().st_size


def test_export_json_report_creates_output_directory(tmp_path, analysis_result):
    output_dir = tmp_path / "nested" / "reports"

    result = export_json_report(
        analysis_result,
        ReportConfig(output_dir=output_dir),
    )

    assert output_dir.exists()
    assert result.output_path.exists()


def test_export_json_report_uses_custom_filename(tmp_path, analysis_result):
    config = ReportConfig(
        output_dir=tmp_path,
        filename="sales_analysis.json",
    )

    result = export_json_report(analysis_result, config)

    assert result.output_path.name == "sales_analysis.json"


def test_export_json_report_appends_json_extension(tmp_path, analysis_result):
    config = ReportConfig(
        output_dir=tmp_path,
        filename="sales_analysis",
    )

    result = export_json_report(analysis_result, config)

    assert result.output_path.name == "sales_analysis.json"


def test_export_json_report_rejects_wrong_extension(tmp_path, analysis_result):
    config = ReportConfig(
        output_dir=tmp_path,
        filename="sales_analysis.csv",
    )

    with pytest.raises(ValueError, match="extension"):
        export_json_report(analysis_result, config)


def test_export_json_report_rejects_wrong_format(tmp_path, analysis_result):
    config = ReportConfig(
        output_dir=tmp_path,
        format=ReportFormat.HTML,
    )

    with pytest.raises(ValueError, match="ReportFormat.JSON"):
        export_json_report(analysis_result, config)


def test_export_json_report_rejects_invalid_result(tmp_path):
    with pytest.raises(TypeError, match="AnalysisResult"):
        export_json_report(
            {},
            ReportConfig(output_dir=tmp_path),
        )


def test_export_json_report_rejects_invalid_config(analysis_result):
    with pytest.raises(TypeError, match="ReportConfig"):
        export_json_report(analysis_result, {})


def test_export_json_report_respects_section_configuration(
    tmp_path,
    analysis_result,
):
    config = ReportConfig(
        output_dir=tmp_path,
        include_profile=False,
        include_quality=False,
        include_recommendations=False,
        include_insights=False,
        include_cleaning_summary=False,
    )

    result = export_json_report(analysis_result, config)

    document = json.loads(result.output_path.read_text(encoding="utf-8"))

    assert list(document) == ["metadata"]


def test_export_json_report_includes_selected_sections(
    tmp_path,
    analysis_result,
):
    config = ReportConfig(
        output_dir=tmp_path,
        include_profile=True,
        include_quality=False,
        include_recommendations=True,
        include_insights=False,
        include_cleaning_summary=False,
    )

    result = export_json_report(analysis_result, config)

    document = json.loads(result.output_path.read_text(encoding="utf-8"))

    assert "profile" in document
    assert "quality" not in document
    assert "recommendations" in document
    assert "insights" not in document
    assert "cleaning_summary" not in document


def test_export_json_report_converts_non_finite_values_to_null(
    tmp_path,
    analysis_result,
):
    result = export_json_report(
        analysis_result,
        ReportConfig(output_dir=tmp_path),
    )

    document = json.loads(result.output_path.read_text(encoding="utf-8"))

    mean = document["profile"]["initial"]["columns"][0]["mean"]

    assert mean is None


def test_export_json_report_converts_numpy_values(tmp_path, analysis_result):
    result = export_json_report(
        analysis_result,
        ReportConfig(output_dir=tmp_path),
    )

    document = json.loads(result.output_path.read_text(encoding="utf-8"))

    top_value = document["profile"]["initial"]["columns"][0]["top_values"][0]

    assert top_value == [100, 2]


def test_export_json_report_includes_metadata(tmp_path, analysis_result):
    result = export_json_report(
        analysis_result,
        ReportConfig(output_dir=tmp_path),
    )

    document = json.loads(result.output_path.read_text(encoding="utf-8"))

    assert document["metadata"]["schema_version"] == "1.0"
    assert document["metadata"]["format"] == "json"
    assert document["metadata"]["generated_at"]


def test_export_json_report_returns_section_metadata(
    tmp_path,
    analysis_result,
):
    result = export_json_report(
        analysis_result,
        ReportConfig(output_dir=tmp_path),
    )

    assert result.metadata["source"] == "sample_sales.csv"
    assert "profile" in result.metadata["sections"]
    assert "quality" in result.metadata["sections"]


def test_export_json_report_does_not_modify_dataframe(
    tmp_path,
    analysis_result,
):
    original = analysis_result.dataframe.copy(deep=True)

    export_json_report(
        analysis_result,
        ReportConfig(output_dir=tmp_path),
    )

    pd.testing.assert_frame_equal(analysis_result.dataframe, original)


def test_export_json_report_preserves_quality_properties(
    tmp_path,
    analysis_result,
):
    result = export_json_report(
        analysis_result,
        ReportConfig(output_dir=tmp_path),
    )

    document = json.loads(result.output_path.read_text(encoding="utf-8"))

    assert "has_errors" not in document["quality"]["initial"]
    assert "has_warnings" not in document["quality"]["initial"]
    assert "is_healthy" not in document["quality"]["initial"]


def test_export_json_report_uses_consistent_utc_timestamp(
    tmp_path,
    analysis_result,
):
    result = export_json_report(
        analysis_result,
        ReportConfig(output_dir=tmp_path),
    )

    document = json.loads(result.output_path.read_text(encoding="utf-8"))

    report_timestamp = document["metadata"]["generated_at"]
    result_timestamp = result.generated_at.isoformat()

    assert report_timestamp == result_timestamp
    assert result.generated_at.tzinfo is not None
    assert result.generated_at.utcoffset().total_seconds() == 0


@pytest.mark.parametrize(
    "filename",
    [
        "../report.json",
        "..\\report.json",
        "C:\\reports\\report.json",
        "/reports/report.json",
        ".",
        "..",
        "",
        123,
    ],
)
def test_export_json_report_rejects_modified_unsafe_filename(
    tmp_path,
    analysis_result,
    filename,
):
    config = ReportConfig(output_dir=tmp_path)
    config.filename = filename

    with pytest.raises((TypeError, ValueError)):
        export_json_report(analysis_result, config)

    assert list(tmp_path.iterdir()) == []


def test_export_json_report_preserves_existing_file_on_serialization_failure(
    tmp_path,
    analysis_result,
    monkeypatch,
):
    from aladdin.reporting import exporter

    output_path = tmp_path / "analysis_report.json"
    original_content = '{"existing": true}'

    output_path.write_text(original_content, encoding="utf-8")

    monkeypatch.setattr(
        exporter,
        "_build_report_document",
        lambda result, config, generated_at: {"invalid": object()},
    )

    with pytest.raises(TypeError, match="not JSON serializable"):
        export_json_report(
            analysis_result,
            ReportConfig(output_dir=tmp_path),
        )

    assert output_path.read_text(encoding="utf-8") == original_content

    remaining_files = list(tmp_path.iterdir())
    assert remaining_files == [output_path]


def test_export_json_report_cleans_up_temp_file_on_replace_failure(
    tmp_path,
    analysis_result,
    monkeypatch,
):
    from aladdin.reporting import exporter

    output_path = tmp_path / "analysis_report.json"
    original_content = '{"existing": true}'

    output_path.write_text(original_content, encoding="utf-8")

    def fail_replace(source, destination):
        raise PermissionError("Simulated file replacement failure.")

    monkeypatch.setattr(exporter.os, "replace", fail_replace)

    with pytest.raises(PermissionError, match="replacement failure"):
        export_json_report(
            analysis_result,
            ReportConfig(output_dir=tmp_path),
        )

    assert output_path.read_text(encoding="utf-8") == original_content
    assert list(tmp_path.iterdir()) == [output_path]


class SampleStatus(Enum):
    SUCCESS = "success"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2026, 11, 11), "2026-11-11"),
        (datetime(2026, 11, 11, 9, 30), "2026-11-11T09:30:00"),
        (time(9, 30), "09:30:00"),
        (Path("reports/analysis.json"), str(Path("reports/analysis.json"))),
        (SampleStatus.SUCCESS, "success"),
    ],
)
def test_to_json_safe_converts_standard_python_types(value, expected):
    assert _to_json_safe(value) == expected


def test_to_json_safe_converts_pandas_values():
    assert _to_json_safe(pd.Timestamp("2026-11-11")) == "2026-11-11T00:00:00"
    assert _to_json_safe(pd.Timedelta(days=1)) == "1 days 00:00:00"
    assert _to_json_safe(pd.Series([1, 2])) == [1, 2]
    assert _to_json_safe(pd.Index(["a", "b"])) == ["a", "b"]


@pytest.mark.parametrize("value", [pd.NA, pd.NaT, None])
def test_to_json_safe_converts_missing_values(value):
    assert _to_json_safe(value) is None


def test_to_json_safe_converts_numpy_arrays():
    value = np.array([[1, 2], [3, 4]])

    assert _to_json_safe(value) == [[1, 2], [3, 4]]


def test_to_json_safe_converts_nested_structures():
    value = {
        "numbers": (np.int64(10), np.float64(2.5)),
        "tags": {"alpha", "beta"},
        "path": Path("data/sample.csv"),
    }

    result = _to_json_safe(value)

    assert result["numbers"] == [10, 2.5]
    assert result["tags"] == ["alpha", "beta"]
    assert result["path"] == str(Path("data/sample.csv"))


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_to_json_safe_converts_non_finite_floats(value):
    assert _to_json_safe(value) is None


def test_to_json_safe_preserves_finite_floats():
    assert _to_json_safe(12.5) == 12.5


def test_to_json_safe_rejects_unsupported_objects():
    with pytest.raises(
        TypeError,
        match="Unsupported JSON serialization type",
    ):
        _to_json_safe(object())


def test_to_json_safe_rejects_dataframes():
    dataframe = pd.DataFrame({"value": [1, 2, 3]})

    with pytest.raises(
        TypeError,
        match="DataFrames cannot be serialized",
    ):
        _to_json_safe(dataframe)
