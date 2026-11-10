from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class ChartType(StrEnum):
    """Supported chart types."""

    HISTOGRAM = "histogram"
    BAR = "bar"
    MISSING_VALUES = "missing_values"
    CORRELATION_HEATMAP = "correlation_heatmap"


@dataclass
class ChartResult:
    """Represents a generated visualization."""

    chart_type: ChartType
    title: str
    figure: Any
    output_path: Path | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Validate chart result fields."""

        if not isinstance(self.chart_type, ChartType):
            raise TypeError("chart_type must be a ChartType.")

        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title must be a non-empty string.")

        if self.output_path is not None:
            if not isinstance(self.output_path, (str, Path)):
                raise TypeError("output_path must be a string or Path.")

            self.output_path = Path(self.output_path)

        if self.metadata is None:
            self.metadata = {}
        elif not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")
