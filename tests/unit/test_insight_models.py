import pytest

from aladdin.insights.models import (
    DataInsight,
    InsightCategory,
    InsightPriority,
    InsightReport,
)


def create_sample_insight() -> DataInsight:
    return DataInsight(
        code="NUMERIC_MEAN",
        title="High average value",
        description="The average value of the column is relatively high.",
        category=InsightCategory.NUMERIC,
        priority=InsightPriority.MEDIUM,
        column_name="sales",
        evidence={"mean": 1500.0},
    )


def test_data_insight_creation():
    insight = create_sample_insight()

    assert insight.code == "NUMERIC_MEAN"
    assert insight.category == InsightCategory.NUMERIC
    assert insight.priority == InsightPriority.MEDIUM
    assert insight.evidence["mean"] == 1500.0


@pytest.mark.parametrize(
    "field,value",
    [
        ("code", ""),
        ("title", ""),
        ("description", ""),
    ],
)
def test_data_insight_rejects_empty_required_strings(field, value):
    values = {
        "code": "NUMERIC_MEAN",
        "title": "High average value",
        "description": "An analytical observation.",
        "category": InsightCategory.NUMERIC,
        "priority": InsightPriority.MEDIUM,
    }

    values[field] = value

    with pytest.raises(ValueError):
        DataInsight(**values)


def test_data_insight_rejects_invalid_category():
    with pytest.raises(TypeError, match="InsightCategory"):
        DataInsight(
            code="TEST",
            title="Test",
            description="Test description",
            category="numeric",
            priority=InsightPriority.LOW,
        )


def test_data_insight_rejects_invalid_evidence():
    with pytest.raises(TypeError, match="evidence"):
        DataInsight(
            code="TEST",
            title="Test",
            description="Test description",
            category=InsightCategory.NUMERIC,
            priority=InsightPriority.LOW,
            evidence=[],
        )


def test_insight_report_creation():
    insight = create_sample_insight()

    report = InsightReport(
        row_count=100,
        column_count=5,
        insights=[insight],
    )

    assert report.has_insights
    assert report.insight_count == 1
    assert report.high_priority_count == 0


def test_insight_report_empty():
    report = InsightReport(
        row_count=0,
        column_count=0,
    )

    assert not report.has_insights
    assert report.insight_count == 0
    assert report.high_priority_count == 0


@pytest.mark.parametrize(
    "row_count,column_count",
    [
        (-1, 2),
        (2, -1),
        (True, 2),
        (2, False),
    ],
)
def test_insight_report_rejects_invalid_dimensions(row_count, column_count):
    with pytest.raises(ValueError):
        InsightReport(
            row_count=row_count,
            column_count=column_count,
        )


def test_insight_report_rejects_invalid_insights():
    with pytest.raises(TypeError, match="DataInsight"):
        InsightReport(
            row_count=10,
            column_count=2,
            insights=["invalid"],
        )
