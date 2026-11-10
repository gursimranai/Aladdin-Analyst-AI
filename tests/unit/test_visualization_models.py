import pytest

from aladdin.visualization.config import VisualizationConfig
from aladdin.visualization.models import ChartResult, ChartType


def test_default_visualization_config():
    config = VisualizationConfig()

    assert config.width == 10.0
    assert config.height == 6.0
    assert config.dpi == 100
    assert config.output_format == "png"
    assert config.show is False
    assert config.save is False
    assert config.output_dir is None


def test_visualization_config_normalizes_output_format():
    config = VisualizationConfig(output_format=" PNG ")

    assert config.output_format == "png"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"width": 0},
        {"width": -1},
        {"height": 0},
        {"height": -1},
        {"dpi": 0},
        {"dpi": -1},
        {"output_format": "gif"},
        {"save": True},
    ],
)
def test_visualization_config_rejects_invalid_values(kwargs):
    with pytest.raises((TypeError, ValueError)):
        VisualizationConfig(**kwargs)


def test_visualization_config_accepts_output_directory(tmp_path):
    config = VisualizationConfig(
        save=True,
        output_dir=tmp_path,
    )

    assert config.output_dir == tmp_path


def test_chart_result_initializes_metadata():
    result = ChartResult(
        chart_type=ChartType.HISTOGRAM,
        title="Sales Distribution",
        figure=None,
    )

    assert result.metadata == {}
    assert result.output_path is None


def test_chart_result_accepts_output_path(tmp_path):
    output_path = tmp_path / "sales.png"

    result = ChartResult(
        chart_type=ChartType.HISTOGRAM,
        title="Sales Distribution",
        figure=None,
        output_path=output_path,
    )

    assert result.output_path == output_path


def test_chart_result_rejects_invalid_chart_type():
    with pytest.raises(TypeError):
        ChartResult(
            chart_type="histogram",
            title="Sales",
            figure=None,
        )


def test_chart_result_rejects_empty_title():
    with pytest.raises(ValueError):
        ChartResult(
            chart_type=ChartType.BAR,
            title=" ",
            figure=None,
        )
