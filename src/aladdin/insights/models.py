from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class InsightCategory(StrEnum):
    """Categories of analytical insights."""

    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DISTRIBUTION = "distribution"
    RELATIONSHIP = "relationship"
    DATA_QUALITY = "data_quality"


class InsightPriority(StrEnum):
    """Priority levels for analytical insights."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class DataInsight:
    """Represents an individual finding discovered in a dataset."""

    code: str
    title: str
    description: str

    category: InsightCategory
    priority: InsightPriority

    column_name: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not self.code.strip():
            raise ValueError("code must be a non-empty string.")

        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title must be a non-empty string.")

        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string.")

        if not isinstance(self.category, InsightCategory):
            raise TypeError("category must be an InsightCategory.")

        if not isinstance(self.priority, InsightPriority):
            raise TypeError("priority must be an InsightPriority.")

        if self.column_name is not None and not isinstance(self.column_name, str):
            raise TypeError("column_name must be a string or None.")

        if not isinstance(self.evidence, dict):
            raise TypeError("evidence must be a dictionary.")


@dataclass
class InsightReport:
    """Contains all analytical insights discovered in a dataset."""

    row_count: int
    column_count: int

    insights: list[DataInsight] = field(default_factory=list)

    def __post_init__(self) -> None:
        for name, value in (
            ("row_count", self.row_count),
            ("column_count", self.column_count),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer.")

        if not isinstance(self.insights, list):
            raise TypeError("insights must be a list.")

        if not all(isinstance(item, DataInsight) for item in self.insights):
            raise TypeError("Every insight must be a DataInsight.")

    @property
    def has_insights(self) -> bool:
        """Return whether any insights were generated."""

        return bool(self.insights)

    @property
    def high_priority_count(self) -> int:
        """Return the number of high-priority insights."""

        return sum(item.priority == InsightPriority.HIGH for item in self.insights)

    @property
    def insight_count(self) -> int:
        """Return the total number of generated insights."""

        return len(self.insights)
