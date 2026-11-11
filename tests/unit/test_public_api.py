import aladdin
from aladdin.reporting import (
    ReportConfig,
    ReportFormat,
    ReportResult,
    export_json_report,
)


def test_package_version():
    assert aladdin.__version__ == "0.1.0"


def test_public_api_exports():
    expected_exports = [
        "load_csv",
        "load_excel",
        "load_json",
        "load_parquet",
        "load_data",
        "profile_data",
        "assess_data_quality",
        "clean_data",
        "analyze_dataframe",
        "analyze_file",
        "AnalysisResult",
        "CleaningConfig",
        "DataProfile",
        "DataQualityReport",
    ]

    for name in expected_exports:
        assert hasattr(aladdin, name), f"Missing public API: {name}"


def test_pipeline_functions_are_importable():
    from aladdin import analyze_dataframe, analyze_file

    assert callable(analyze_dataframe)
    assert callable(analyze_file)


def test_reporting_api_is_available_from_root_package():
    assert aladdin.ReportConfig is ReportConfig
    assert aladdin.ReportFormat is ReportFormat
    assert aladdin.ReportResult is ReportResult
    assert aladdin.export_json_report is export_json_report


def test_reporting_api_is_in_root_all():
    expected = {
        "ReportConfig",
        "ReportFormat",
        "ReportResult",
        "export_json_report",
    }

    assert expected.issubset(set(aladdin.__all__))
