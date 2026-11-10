from pathlib import Path
from typing import Any

import pandas as pd

from aladdin.cleaning.cleaner import clean_data
from aladdin.cleaning.models import CleaningConfig
from aladdin.ingestion.loader import load_data
from aladdin.logging_config import get_logger
from aladdin.pipeline.models import AnalysisResult
from aladdin.profiling.profiler import profile_data
from aladdin.quality.assessor import assess_data_quality

logger = get_logger("pipeline.analyzer")


def analyze_dataframe(
    dataframe: pd.DataFrame,
    cleaning_config: CleaningConfig | None = None,
    top_n: int = 5,
) -> AnalysisResult:
    """
    Run the complete analysis workflow on an existing DataFrame.

    The original DataFrame is not modified.
    """

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")

    logger.info(
        "Starting dataset analysis | rows=%d | columns=%d",
        len(dataframe),
        len(dataframe.columns),
    )

    # Step 1: Analyze the original dataset.
    initial_profile = profile_data(dataframe, top_n=top_n)
    initial_quality_report = assess_data_quality(dataframe)

    # Step 2: Apply explicitly configured cleaning operations.
    cleaning_result = clean_data(
        dataframe,
        config=cleaning_config,
    )

    cleaned_dataframe = cleaning_result.dataframe

    # Step 3: Analyze the cleaned dataset.
    final_profile = profile_data(
        cleaned_dataframe,
        top_n=top_n,
    )
    final_quality_report = assess_data_quality(cleaned_dataframe)

    result = AnalysisResult(
        initial_profile=initial_profile,
        initial_quality_report=initial_quality_report,
        cleaning_result=cleaning_result,
        final_profile=final_profile,
        final_quality_report=final_quality_report,
    )

    logger.info(
        "Dataset analysis completed | initial_rows=%d | final_rows=%d",
        initial_profile.row_count,
        final_profile.row_count,
    )

    return result


def analyze_file(
    file_path: str | Path,
    cleaning_config: CleaningConfig | None = None,
    top_n: int = 5,
    **read_kwargs: Any,
) -> AnalysisResult:
    """
    Load a supported data file and run the complete analysis workflow.

    Additional keyword arguments are forwarded to the selected loader.
    """

    path = Path(file_path)

    logger.info("Starting file analysis: %s", path)

    dataframe = load_data(
        path,
        **read_kwargs,
    )

    result = analyze_dataframe(
        dataframe,
        cleaning_config=cleaning_config,
        top_n=top_n,
    )

    result.source = str(path)

    return result
