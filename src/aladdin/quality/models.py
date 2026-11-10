from dataclasses import dataclass, field
from enum import StrEnum


class IssueSeverity(StrEnum):
    """Severity levels for data quality issues."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class DataQualityIssue:
    """Represents an individual data quality issue."""

    code: str
    severity: IssueSeverity
    message: str

    column_name: str | None = None
    affected_count: int | None = None
    affected_columns: list[str] = field(default_factory=list)


@dataclass
class DataQualityReport:
    """Structured report containing dataset quality findings."""

    row_count: int
    column_count: int
    issues: list[DataQualityIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Return whether the report contains errors."""

        return any(issue.severity == IssueSeverity.ERROR for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        """Return whether the report contains warnings."""

        return any(issue.severity == IssueSeverity.WARNING for issue in self.issues)

    @property
    def is_healthy(self) -> bool:
        """Return whether the dataset has no warnings or errors."""

        return not self.has_errors and not self.has_warnings
