"""Export analysis results into structured JSON reports."""

import json
import math
import os
import tempfile
from dataclasses import fields, is_dataclass
from datetime import UTC, date, datetime, time
from enum import Enum
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

import numpy as np
import pandas as pd

from aladdin.logging_config import get_logger
from aladdin.pipeline.models import AnalysisResult
from aladdin.reporting.models import ReportConfig, ReportFormat, ReportResult

logger = get_logger(__name__)


def _to_json_safe(value: Any) -> Any:
    """Convert supported Python, Pandas, and NumPy values into JSON-safe values."""

    if value is None or value is pd.NA or value is pd.NaT:
        return None

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, (pd.Timestamp, datetime, date, time)):
        return value.isoformat()

    if isinstance(value, (pd.Timedelta,)):
        return str(value)

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, np.ndarray):
        return [_to_json_safe(item) for item in value.tolist()]

    if isinstance(value, (pd.Series, pd.Index)):
        return [_to_json_safe(item) for item in value.tolist()]

    if isinstance(value, np.generic):
        return _to_json_safe(value.item())

    if isinstance(value, float):
        return value if math.isfinite(value) else None

    if isinstance(value, (str, int, bool)):
        return value

    if is_dataclass(value) and not isinstance(value, type):
        return {
            item.name: _to_json_safe(getattr(value, item.name))
            for item in fields(value)
        }

    if isinstance(value, dict):
        return {
            str(_to_json_safe(key)): _to_json_safe(item) for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_to_json_safe(item) for item in value]

    if isinstance(value, set):
        return [_to_json_safe(item) for item in sorted(value, key=repr)]

    if isinstance(value, pd.DataFrame):
        raise TypeError(
            "DataFrames cannot be serialized as report sections. "
            "Use the CSV exporter for tabular data."
        )

    raise TypeError(f"Unsupported JSON serialization type: {type(value).__name__}")


def _validate_report_filename(filename: str) -> None:
    """Validate a report filename before writing to the filesystem."""

    if not isinstance(filename, str):
        raise TypeError("filename must be a string.")

    if not filename.strip():
        raise ValueError("filename cannot be empty.")

    if (
        filename in {".", ".."}
        or PurePosixPath(filename).name != filename
        or PureWindowsPath(filename).name != filename
        or PureWindowsPath(filename).drive
    ):
        raise ValueError("filename must be a filename without directory paths.")


def _build_report_document(
    result: AnalysisResult,
    config: ReportConfig,
    generated_at: datetime,
) -> dict[str, Any]:
    """Build the JSON report using the sections enabled in the configuration."""

    report: dict[str, Any] = {
        "metadata": {
            "schema_version": "1.0",
            "generated_at": generated_at.isoformat(),
            "source": result.source,
            "format": ReportFormat.JSON.value,
        }
    }

    if config.include_profile:
        report["profile"] = {
            "initial": _to_json_safe(result.initial_profile),
            "final": _to_json_safe(result.final_profile),
        }

    if config.include_quality:
        report["quality"] = {
            "initial": _to_json_safe(result.initial_quality_report),
            "final": _to_json_safe(result.final_quality_report),
        }

    if config.include_recommendations:
        report["recommendations"] = _to_json_safe(result.recommendations)

    if config.include_insights:
        report["insights"] = _to_json_safe(result.insights)

    if config.include_cleaning_summary:
        report["cleaning_summary"] = _to_json_safe(result.cleaning_result.report)

    return report


def _write_json_atomically(
    report_document: dict[str, Any],
    output_path: Path,
) -> None:
    """Write a JSON report atomically to avoid incomplete destination files."""

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

            json.dump(
                report_document,
                temporary_file,
                indent=4,
                ensure_ascii=False,
                allow_nan=False,
            )

            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, output_path)

    finally:
        if temporary_path is not None and temporary_path.exists():
            try:
                temporary_path.unlink()
            except OSError:
                logger.warning(
                    "Could not remove temporary report file: %s",
                    temporary_path,
                )


def export_json_report(
    result: AnalysisResult,
    config: ReportConfig,
) -> ReportResult:
    """Export an AnalysisResult as a structured JSON report."""

    if not isinstance(result, AnalysisResult):
        raise TypeError("result must be an AnalysisResult.")

    if not isinstance(config, ReportConfig):
        raise TypeError("config must be a ReportConfig.")

    if config.format != ReportFormat.JSON:
        raise ValueError("config.format must be ReportFormat.JSON.")

    filename = "analysis_report" if config.filename is None else config.filename

    _validate_report_filename(filename)

    filename_path = Path(filename)

    if filename_path.suffix and filename_path.suffix.lower() != ".json":
        raise ValueError("JSON report filenames must use the .json extension.")

    if not filename_path.suffix:
        filename = f"{filename}.json"

    output_dir = config.output_dir
    output_path = output_dir / filename

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_at = datetime.now(UTC)

        output_dir.mkdir(parents=True, exist_ok=True)

        generated_at = datetime.now(UTC)

        report_document = _build_report_document(
            result,
            config,
            generated_at,
        )

        _write_json_atomically(report_document, output_path)
        file_size = output_path.stat().st_size

        logger.info("JSON report exported successfully: %s", output_path)

        return ReportResult(
            format=ReportFormat.JSON,
            output_path=output_path,
            file_size_bytes=file_size,
            generated_at=generated_at,
            metadata={
                "sections": [
                    section for section in report_document if section != "metadata"
                ],
                "source": result.source,
            },
        )

    except (OSError, TypeError, ValueError):
        logger.exception("Failed to export JSON report: %s", output_path)
        raise
