from dataclasses import dataclass, field
from enum import StrEnum

from aladdin.cleaning.models import MissingValueStrategy


class RecommendationAction(StrEnum):
    """Actions that the recommendation engine can suggest."""

    FILL_MISSING_VALUES = "fill_missing_values"
    DROP_DUPLICATE_ROWS = "drop_duplicate_rows"
    DROP_CONSTANT_COLUMN = "drop_constant_column"
    MANUAL_REVIEW = "manual_review"


class RecommendationPriority(StrEnum):
    """Priority levels for data cleaning recommendations."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class CleaningRecommendation:
    """Represents a suggested data cleaning action."""

    code: str
    title: str
    description: str

    action: RecommendationAction
    priority: RecommendationPriority

    column_name: str | None = None
    affected_count: int | None = None

    suggested_strategy: MissingValueStrategy | None = None
    requires_approval: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not self.code.strip():
            raise ValueError("code must be a non-empty string.")

        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title must be a non-empty string.")

        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string.")

        if not isinstance(self.action, RecommendationAction):
            raise TypeError("action must be a RecommendationAction.")

        if not isinstance(self.priority, RecommendationPriority):
            raise TypeError("priority must be a RecommendationPriority.")

        if self.column_name is not None and not isinstance(self.column_name, str):
            raise TypeError("column_name must be a string or None.")

        if self.affected_count is not None:
            if (
                not isinstance(self.affected_count, int)
                or isinstance(self.affected_count, bool)
                or self.affected_count < 0
            ):
                raise ValueError("affected_count must be a non-negative integer.")

        if self.suggested_strategy is not None:
            if not isinstance(self.suggested_strategy, MissingValueStrategy):
                raise TypeError(
                    "suggested_strategy must be a MissingValueStrategy or None."
                )

        if not isinstance(self.requires_approval, bool):
            raise TypeError("requires_approval must be a boolean.")


@dataclass
class RecommendationReport:
    """Contains all cleaning recommendations for a dataset."""

    row_count: int
    column_count: int

    recommendations: list[CleaningRecommendation] = field(default_factory=list)

    def __post_init__(self) -> None:
        for name, value in (
            ("row_count", self.row_count),
            ("column_count", self.column_count),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer.")

        if not isinstance(self.recommendations, list):
            raise TypeError("recommendations must be a list.")

        if not all(
            isinstance(item, CleaningRecommendation) for item in self.recommendations
        ):
            raise TypeError("Every recommendation must be a CleaningRecommendation.")

    @property
    def has_recommendations(self) -> bool:
        """Return whether any recommendations were generated."""

        return bool(self.recommendations)

    @property
    def requires_approval(self) -> bool:
        """Return whether any recommendation requires user approval."""

        return any(item.requires_approval for item in self.recommendations)

    @property
    def high_priority_count(self) -> int:
        """Return the number of high-priority recommendations."""

        return sum(
            item.priority == RecommendationPriority.HIGH
            for item in self.recommendations
        )
