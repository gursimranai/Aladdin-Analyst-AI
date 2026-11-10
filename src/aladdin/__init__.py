from aladdin.cleaning import (
    CleaningConfig,
    CleaningReport,
    CleaningResult,
    MissingValueConfig,
    MissingValueStrategy,
    clean_data,
)
from aladdin.ingestion import (
    load_csv,
    load_data,
    load_excel,
    load_json,
    load_parquet,
)
from aladdin.insights import (
    DataInsight,
    InsightCategory,
    InsightPriority,
    InsightReport,
    generate_insights,
)
from aladdin.pipeline import (
    AnalysisResult,
    analyze_dataframe,
    analyze_file,
)
from aladdin.profiling import (
    ColumnProfile,
    DataProfile,
    profile_data,
)
from aladdin.quality import (
    DataQualityIssue,
    DataQualityReport,
    IssueSeverity,
    assess_data_quality,
)
from aladdin.recommendations import (
    CleaningRecommendation,
    RecommendationAction,
    RecommendationPriority,
    RecommendationReport,
    recommend_cleaning,
)

__version__ = "0.1.0"


__all__ = [
    "__version__",
    # Ingestion
    "load_csv",
    "load_excel",
    "load_json",
    "load_parquet",
    "load_data",
    # Profiling
    "ColumnProfile",
    "DataProfile",
    "profile_data",
    # Quality
    "DataQualityIssue",
    "DataQualityReport",
    "IssueSeverity",
    "assess_data_quality",
    # Cleaning
    "CleaningConfig",
    "CleaningReport",
    "CleaningResult",
    "MissingValueConfig",
    "MissingValueStrategy",
    "clean_data",
    # Pipeline
    "AnalysisResult",
    "analyze_dataframe",
    "analyze_file",
    # Recommendations
    "CleaningRecommendation",
    "RecommendationAction",
    "RecommendationPriority",
    "RecommendationReport",
    "recommend_cleaning",
    "DataInsight",
    "InsightCategory",
    "InsightPriority",
    "InsightReport",
    "generate_insights",
]
