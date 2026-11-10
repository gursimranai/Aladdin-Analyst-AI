import aladdin


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
