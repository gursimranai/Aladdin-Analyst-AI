from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


class ReportFormat(StrEnum):
    JSON = "json"
    HTML = "html"
    CSV = "csv"


@dataclass
class ReportConfig:
    output_dir: str | Path
    format: ReportFormat = ReportFormat.JSON
    filename: str | None = None
    include_profile: bool = True
    include_quality: bool = True
    include_recommendations: bool = True
    include_insights: bool = True
    include_cleaning_summary: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.output_dir, (str, Path)):
            raise TypeError("output_dir must be a string or Path.")

        self.output_dir = Path(self.output_dir)

        if not isinstance(self.format, ReportFormat):
            raise TypeError("format must be a ReportFormat.")

        if self.filename is not None:
            if not isinstance(self.filename, str):
                raise TypeError("filename must be a string or None.")

            if not self.filename.strip():
                raise ValueError("filename cannot be empty.")

            if (
                self.filename in {".", ".."}
                or PurePosixPath(self.filename).name != self.filename
                or PureWindowsPath(self.filename).name != self.filename
                or PureWindowsPath(self.filename).drive
            ):
                raise ValueError("filename must be a filename without directory paths.")

        boolean_fields = [
            self.include_profile,
            self.include_quality,
            self.include_recommendations,
            self.include_insights,
            self.include_cleaning_summary,
        ]

        if not all(isinstance(value, bool) for value in boolean_fields):
            raise TypeError("All include options must be boolean values.")


@dataclass
class ReportResult:
    format: ReportFormat
    output_path: Path
    file_size_bytes: int
    generated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.format, ReportFormat):
            raise TypeError("format must be a ReportFormat.")

        if not isinstance(self.output_path, (str, Path)):
            raise TypeError("output_path must be a string or Path.")

        self.output_path = Path(self.output_path)

        if (
            isinstance(self.file_size_bytes, bool)
            or not isinstance(self.file_size_bytes, int)
            or self.file_size_bytes < 0
        ):
            raise ValueError("file_size_bytes must be a non-negative integer.")

        if not isinstance(self.generated_at, datetime):
            raise TypeError("generated_at must be a datetime.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")
