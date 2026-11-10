from dataclasses import dataclass

import pandas as pd

from aladdin.cleaning.models import CleaningResult
from aladdin.insights.models import InsightReport
from aladdin.profiling.models import DataProfile
from aladdin.quality.models import DataQualityReport
from aladdin.recommendations.models import RecommendationReport


@dataclass
class AnalysisResult:
    """Complete result of an Aladdin dataset analysis workflow."""

    initial_profile: DataProfile
    initial_quality_report: DataQualityReport
    recommendations: RecommendationReport
    insights: InsightReport

    cleaning_result: CleaningResult

    final_profile: DataProfile
    final_quality_report: DataQualityReport

    source: str | None = None

    @property
    def dataframe(self) -> pd.DataFrame:
        """Return the final cleaned DataFrame."""

        return self.cleaning_result.dataframe
