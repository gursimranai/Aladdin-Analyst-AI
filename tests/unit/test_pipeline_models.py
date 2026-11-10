import pandas as pd

from aladdin.cleaning.models import CleaningReport, CleaningResult
from aladdin.insights.models import InsightReport
from aladdin.pipeline.models import AnalysisResult
from aladdin.profiling.models import DataProfile
from aladdin.quality.models import DataQualityReport
from aladdin.recommendations.models import RecommendationReport


def test_analysis_result_stores_all_components():
    dataframe = pd.DataFrame({"age": [20, 30, 40]})

    cleaning_report = CleaningReport(
        rows_before=3,
        rows_after=3,
        columns_before=1,
        columns_after=1,
        missing_values_before=0,
        missing_values_after=0,
    )

    cleaning_result = CleaningResult(
        dataframe=dataframe,
        report=cleaning_report,
    )

    profile = DataProfile(
        row_count=3,
        column_count=1,
        duplicate_rows=0,
        columns=[],
    )

    quality_report = DataQualityReport(
        row_count=3,
        column_count=1,
    )

    result = AnalysisResult(
        initial_profile=profile,
        initial_quality_report=quality_report,
        recommendations=RecommendationReport(
            row_count=3,
            column_count=1,
            recommendations=[],
        ),
        insights=InsightReport(
            row_count=3,
            column_count=1,
            insights=[],
        ),
        cleaning_result=cleaning_result,
        final_profile=profile,
        final_quality_report=quality_report,
        source="sample.csv",
    )

    assert result.initial_profile.row_count == 3
    assert result.initial_quality_report.is_healthy
    assert result.cleaning_result.report.rows_after == 3
    assert result.final_profile.row_count == 3
    assert result.final_quality_report.is_healthy
    assert result.source == "sample.csv"


def test_analysis_result_dataframe_property():
    dataframe = pd.DataFrame({"age": [20, 30, 40]})

    cleaning_result = CleaningResult(
        dataframe=dataframe,
        report=CleaningReport(
            rows_before=3,
            rows_after=3,
            columns_before=1,
            columns_after=1,
            missing_values_before=0,
            missing_values_after=0,
        ),
    )

    profile = DataProfile(
        row_count=3,
        column_count=1,
        duplicate_rows=0,
        columns=[],
    )

    quality_report = DataQualityReport(
        row_count=3,
        column_count=1,
    )

    result = AnalysisResult(
        initial_profile=profile,
        initial_quality_report=quality_report,
        recommendations=RecommendationReport(
            row_count=3,
            column_count=1,
            recommendations=[],
        ),
        insights=InsightReport(
            row_count=3,
            column_count=1,
            insights=[],
        ),
        cleaning_result=cleaning_result,
        final_profile=profile,
        final_quality_report=quality_report,
    )

    pd.testing.assert_frame_equal(result.dataframe, dataframe)
