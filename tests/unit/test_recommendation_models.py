import pytest

from aladdin.cleaning.models import MissingValueStrategy
from aladdin.recommendations.models import (
    CleaningRecommendation,
    RecommendationAction,
    RecommendationPriority,
    RecommendationReport,
)


def create_recommendation(**overrides):
    values = {
        "code": "MISSING_VALUES_AGE",
        "title": "Handle missing age values",
        "description": "The age column contains missing values.",
        "action": RecommendationAction.FILL_MISSING_VALUES,
        "priority": RecommendationPriority.MEDIUM,
        "column_name": "age",
        "affected_count": 3,
        "suggested_strategy": MissingValueStrategy.FILL_MEDIAN,
    }

    values.update(overrides)

    return CleaningRecommendation(**values)


def test_create_valid_recommendation():
    recommendation = create_recommendation()

    assert recommendation.code == "MISSING_VALUES_AGE"
    assert recommendation.action == RecommendationAction.FILL_MISSING_VALUES
    assert recommendation.suggested_strategy == MissingValueStrategy.FILL_MEDIAN
    assert recommendation.requires_approval is True


@pytest.mark.parametrize(
    "field,value",
    [
        ("code", ""),
        ("title", ""),
        ("description", ""),
    ],
)
def test_recommendation_rejects_empty_text(field, value):
    with pytest.raises(ValueError):
        create_recommendation(**{field: value})


def test_recommendation_rejects_invalid_action():
    with pytest.raises(TypeError):
        create_recommendation(action="fill_missing_values")


def test_recommendation_rejects_invalid_priority():
    with pytest.raises(TypeError):
        create_recommendation(priority="HIGH")


@pytest.mark.parametrize("value", [-1, 1.5, True])
def test_recommendation_rejects_invalid_affected_count(value):
    with pytest.raises(ValueError):
        create_recommendation(affected_count=value)


def test_recommendation_rejects_invalid_strategy():
    with pytest.raises(TypeError):
        create_recommendation(suggested_strategy="fill_median")


def test_create_empty_recommendation_report():
    report = RecommendationReport(
        row_count=100,
        column_count=5,
    )

    assert report.recommendations == []
    assert report.has_recommendations is False
    assert report.requires_approval is False
    assert report.high_priority_count == 0


def test_recommendation_report_properties():
    recommendations = [
        create_recommendation(
            priority=RecommendationPriority.HIGH,
        ),
        create_recommendation(
            code="MISSING_VALUES_CITY",
            column_name="city",
            priority=RecommendationPriority.MEDIUM,
            requires_approval=False,
        ),
    ]

    report = RecommendationReport(
        row_count=100,
        column_count=5,
        recommendations=recommendations,
    )

    assert report.has_recommendations is True
    assert report.requires_approval is True
    assert report.high_priority_count == 1


def test_recommendation_report_rejects_invalid_counts():
    with pytest.raises(ValueError):
        RecommendationReport(row_count=-1, column_count=5)

    with pytest.raises(ValueError):
        RecommendationReport(row_count=100, column_count=-1)


def test_recommendation_report_rejects_invalid_items():
    with pytest.raises(TypeError):
        RecommendationReport(
            row_count=100,
            column_count=5,
            recommendations=["invalid"],
        )
