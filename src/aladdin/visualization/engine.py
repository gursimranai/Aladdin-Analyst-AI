import re

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from aladdin.visualization.config import VisualizationConfig
from aladdin.visualization.models import ChartResult, ChartType


def _create_figure(config: VisualizationConfig):
    """Create a figure without changing Matplotlib's global backend."""

    try:
        if config.show:
            import matplotlib.pyplot as plt

            figure, axis = plt.subplots(
                figsize=(config.width, config.height),
                dpi=config.dpi,
            )

            return figure, axis, plt

        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure

        figure = Figure(
            figsize=(config.width, config.height),
            dpi=config.dpi,
        )

        FigureCanvasAgg(figure)
        axis = figure.subplots()

        return figure, axis, None

    except ImportError as exc:
        raise ImportError(
            "Visualization support requires Matplotlib. "
            "Install it using: python -m pip install "
            "'aladdin-analyst-ai[visualization]'"
        ) from exc


def _close_figure(figure, pyplot):
    """Clean up a figure after chart-generation failure."""

    if pyplot is not None:
        pyplot.close(figure)
    else:
        figure.clear()


def create_histogram(
    dataframe: pd.DataFrame,
    column: str,
    config: VisualizationConfig | None = None,
    bins: int = 30,
    title: str | None = None,
) -> ChartResult:
    """Generate a histogram for a numerical DataFrame column."""

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("dataframe must be a pandas DataFrame.")

    if not isinstance(column, str) or not column.strip():
        raise ValueError("column must be a non-empty string.")

    if column not in dataframe.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    if list(dataframe.columns).count(column) > 1:
        raise ValueError(f"Column '{column}' has duplicate labels.")

    if isinstance(bins, bool) or not isinstance(bins, int):
        raise TypeError("bins must be an integer.")

    if bins <= 0:
        raise ValueError("bins must be greater than zero.")

    if title is not None:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string.")

    if config is None:
        config = VisualizationConfig()
    elif not isinstance(config, VisualizationConfig):
        raise TypeError("config must be a VisualizationConfig instance.")

    series = dataframe[column]

    if not is_numeric_dtype(series.dtype) or pd.api.types.is_bool_dtype(series.dtype):
        raise TypeError(f"Column '{column}' must contain numerical data.")

    values = series.dropna().to_numpy(dtype=float)

    finite_mask = np.isfinite(values)
    finite_values = values[finite_mask]

    if finite_values.size == 0:
        raise ValueError(f"Column '{column}' contains no finite numerical values.")

    chart_title = title or f"Distribution of {column}"

    figure = None
    plt = None

    try:
        figure, axis, plt = _create_figure(config)

        axis.hist(finite_values, bins=bins, edgecolor="black")

        axis.set_title(chart_title)
        axis.set_xlabel(column)
        axis.set_ylabel("Frequency")

        figure.tight_layout()

        output_path = None

        if config.save:
            config.output_dir.mkdir(parents=True, exist_ok=True)

            safe_column = re.sub(r"[^a-zA-Z0-9_-]+", "_", column).strip("_")
            filename = f"histogram_{safe_column}.{config.output_format}"

            output_path = config.output_dir / filename

            figure.savefig(
                output_path,
                format=config.output_format,
                dpi=config.dpi,
                bbox_inches="tight",
            )

        if config.show:
            plt.show()

        return ChartResult(
            chart_type=ChartType.HISTOGRAM,
            title=chart_title,
            figure=figure,
            output_path=output_path,
            metadata={
                "column": column,
                "bins": bins,
                "observations": int(finite_values.size),
                "excluded_non_finite": int(values.size - finite_values.size),
            },
        )

    except Exception:
        if figure is not None:
            _close_figure(figure, plt)
        raise


def create_bar_chart(
    dataframe: pd.DataFrame,
    column: str,
    config: VisualizationConfig | None = None,
    top_n: int | None = 10,
    title: str | None = None,
    include_missing: bool = True,
) -> ChartResult:
    """Generate a categorical frequency bar chart."""

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("dataframe must be a pandas DataFrame.")

    if not isinstance(column, str) or not column.strip():
        raise ValueError("column must be a non-empty string.")

    if column not in dataframe.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    if list(dataframe.columns).count(column) > 1:
        raise ValueError(f"Column '{column}' has duplicate labels.")

    if top_n is not None:
        if isinstance(top_n, bool) or not isinstance(top_n, int):
            raise TypeError("top_n must be an integer or None.")

        if top_n <= 0:
            raise ValueError("top_n must be greater than zero.")

    if not isinstance(include_missing, bool):
        raise TypeError("include_missing must be a boolean.")

    if title is not None:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string.")

    if config is None:
        config = VisualizationConfig()
    elif not isinstance(config, VisualizationConfig):
        raise TypeError("config must be a VisualizationConfig instance.")

    series = dataframe[column]

    if not (
        pd.api.types.is_object_dtype(series.dtype)
        or pd.api.types.is_string_dtype(series.dtype)
        or isinstance(series.dtype, pd.CategoricalDtype)
    ):
        raise TypeError(f"Column '{column}' must contain categorical data.")

    # Unique internal markers prevent collisions with real category names.
    missing_marker = object()
    other_marker = object()

    values = series.astype("object").tolist()

    if include_missing:
        values = [missing_marker if pd.isna(value) else value for value in values]
    else:
        values = [value for value in values if not pd.isna(value)]

    if not values:
        raise ValueError(f"Column '{column}' contains no categorical values to plot.")

    frequencies = pd.Series(values, dtype="object").value_counts(sort=True)

    aggregated_categories = []

    if top_n is not None and len(frequencies) > top_n:
        top_categories = frequencies.iloc[:top_n]
        remaining = frequencies.iloc[top_n:]

        aggregated_categories = remaining.index.tolist()

        frequencies = top_categories.copy()
        frequencies.loc[other_marker] = int(remaining.sum())

    # Build display labels without changing the original category values.
    actual_labels = {
        str(value)
        for value in frequencies.index
        if value is not missing_marker and value is not other_marker
    }

    def unique_generated_label(base: str) -> str:
        label = base

        while label in actual_labels:
            label = f"{label} [generated]"

        actual_labels.add(label)
        return label

    missing_label = unique_generated_label("Missing (null values)")
    other_label = unique_generated_label("Other (aggregated)")

    labels = []
    metadata_frequencies = []

    for category, count in frequencies.items():
        if category is missing_marker:
            label = missing_label
            kind = "missing"
            metadata_category = None

        elif category is other_marker:
            label = other_label
            kind = "other"
            metadata_category = None

        else:
            label = str(category)
            kind = "category"
            metadata_category = category

        labels.append(label)

        metadata_frequencies.append(
            {
                "category": metadata_category,
                "label": label,
                "count": int(count),
                "kind": kind,
            }
        )

    chart_title = title or f"Distribution of {column}"
    figure = None
    plt = None

    try:
        figure, axis, plt = _create_figure(config)

        axis.bar(labels, frequencies.values)

        axis.set_title(chart_title)
        axis.set_xlabel(column)
        axis.set_ylabel("Frequency")

        axis.tick_params(axis="x", rotation=45)
        figure.tight_layout()

        output_path = None

        if config.save:
            config.output_dir.mkdir(parents=True, exist_ok=True)

            safe_column = re.sub(r"[^a-zA-Z0-9_-]+", "_", column).strip("_")

            filename = f"bar_{safe_column}.{config.output_format}"
            output_path = config.output_dir / filename

            figure.savefig(
                output_path,
                format=config.output_format,
                dpi=config.dpi,
                bbox_inches="tight",
            )

        if config.show:
            plt.show()

        return ChartResult(
            chart_type=ChartType.BAR,
            title=chart_title,
            figure=figure,
            output_path=output_path,
            metadata={
                "column": column,
                "categories": len(frequencies),
                "observations": len(values),
                "include_missing": include_missing,
                "frequencies": metadata_frequencies,
                "aggregated_categories": aggregated_categories,
            },
        )

    except Exception:
        if figure is not None:
            _close_figure(figure, plt)
        raise


def create_missing_values_chart(
    dataframe: pd.DataFrame,
    config: VisualizationConfig | None = None,
    title: str | None = None,
    include_zero_missing: bool = False,
) -> ChartResult:
    """Generate a bar chart showing missing values in DataFrame columns."""

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("dataframe must be a pandas DataFrame.")

    if len(dataframe.columns) == 0:
        raise ValueError("dataframe must contain at least one column.")

    if not dataframe.columns.is_unique:
        raise ValueError(
            "DataFrame contains duplicate column labels. "
            "Resolve them before generating this chart."
        )

    if not isinstance(include_zero_missing, bool):
        raise TypeError("include_zero_missing must be a boolean.")

    if title is not None:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string.")

    if config is None:
        config = VisualizationConfig()
    elif not isinstance(config, VisualizationConfig):
        raise TypeError("config must be a VisualizationConfig instance.")

    missing_counts = dataframe.isna().sum()

    if not include_zero_missing:
        missing_counts = missing_counts[missing_counts > 0]

    if missing_counts.empty:
        raise ValueError(
            "No missing values found in the DataFrame. "
            "Set include_zero_missing=True to display zero counts."
        )

    records = [
        {
            "column": column,
            "label": str(column),
            "missing_count": int(count),
        }
        for column, count in missing_counts.items()
    ]

    labels = [record["label"] for record in records]
    counts = [record["missing_count"] for record in records]

    chart_title = title or "Missing Values by Column"
    figure = None
    plt = None

    try:
        figure, axis, plt = _create_figure(config)

        axis.bar(labels, counts, edgecolor="black")

        axis.set_title(chart_title)
        axis.set_xlabel("Columns")
        axis.set_ylabel("Missing Values")

        axis.tick_params(axis="x", rotation=45)
        axis.set_ylim(bottom=0)

        figure.tight_layout()

        output_path = None

        if config.save:
            config.output_dir.mkdir(parents=True, exist_ok=True)

            filename = f"missing_values.{config.output_format}"
            output_path = config.output_dir / filename

            figure.savefig(
                output_path,
                format=config.output_format,
                dpi=config.dpi,
                bbox_inches="tight",
            )

        if config.show:
            plt.show()

        return ChartResult(
            chart_type=ChartType.MISSING_VALUES,
            title=chart_title,
            figure=figure,
            output_path=output_path,
            metadata={
                "columns_analyzed": len(dataframe.columns),
                "columns_displayed": len(records),
                "total_missing_values": int(sum(counts)),
                "include_zero_missing": include_zero_missing,
                "missing_counts": records,
            },
        )

    except Exception:
        if figure is not None:
            _close_figure(figure, plt)
        raise


def create_correlation_heatmap(
    dataframe: pd.DataFrame,
    config: VisualizationConfig | None = None,
    title: str | None = None,
) -> ChartResult:
    """Generate a Pearson correlation heatmap for numerical columns."""

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("dataframe must be a pandas DataFrame.")

    if not dataframe.columns.is_unique:
        raise ValueError(
            "DataFrame contains duplicate column labels. "
            "Resolve them before generating this chart."
        )

    if title is not None:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string.")

    if config is None:
        config = VisualizationConfig()
    elif not isinstance(config, VisualizationConfig):
        raise TypeError("config must be a VisualizationConfig instance.")

    numeric_columns = [
        column
        for column in dataframe.columns
        if is_numeric_dtype(dataframe[column].dtype)
        and not pd.api.types.is_bool_dtype(dataframe[column].dtype)
    ]

    if len(numeric_columns) < 2:
        raise ValueError("At least two numerical columns are required.")

    numeric_data = dataframe[numeric_columns].copy()

    # Infinity is not valid input for Pearson correlation.
    numeric_data = numeric_data.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    usable_columns = []

    for column in numeric_columns:
        values = numeric_data[column].to_numpy(
            dtype=float,
            na_value=np.nan,
        )

        finite_values = values[np.isfinite(values)]

        if finite_values.size >= 2 and np.unique(finite_values).size >= 2:
            usable_columns.append(column)

    if len(usable_columns) < 2:
        raise ValueError(
            "At least two non-constant numerical columns with "
            "sufficient finite observations are required."
        )

    numeric_data = numeric_data[usable_columns]

    correlation_matrix = numeric_data.corr(
        method="pearson",
        min_periods=2,
    )

    matrix = correlation_matrix.to_numpy(dtype=float)

    chart_title = title or "Numerical Feature Correlation"
    figure = None
    plt = None

    try:
        figure, axis, plt = _create_figure(config)

        masked_matrix = np.ma.masked_invalid(matrix)

        image = axis.imshow(
            masked_matrix,
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
        )

        labels = [str(column) for column in usable_columns]

        axis.set_xticks(range(len(labels)))
        axis.set_yticks(range(len(labels)))

        axis.set_xticklabels(labels, rotation=45, ha="right")
        axis.set_yticklabels(labels)

        axis.set_title(chart_title)

        figure.colorbar(
            image,
            ax=axis,
            label="Pearson Correlation",
        )

        figure.tight_layout()

        output_path = None

        if config.save:
            config.output_dir.mkdir(parents=True, exist_ok=True)

            filename = f"correlation_heatmap.{config.output_format}"
            output_path = config.output_dir / filename

            figure.savefig(
                output_path,
                format=config.output_format,
                dpi=config.dpi,
                bbox_inches="tight",
            )

        if config.show:
            plt.show()

        correlation_records = []

        for row_index, row_column in enumerate(usable_columns):
            for column_index, column_column in enumerate(usable_columns):
                value = matrix[row_index, column_index]

                correlation_records.append(
                    {
                        "column_1": row_column,
                        "column_2": column_column,
                        "correlation": (float(value) if np.isfinite(value) else None),
                    }
                )

        return ChartResult(
            chart_type=ChartType.CORRELATION_HEATMAP,
            title=chart_title,
            figure=figure,
            output_path=output_path,
            metadata={
                "method": "pearson",
                "columns": usable_columns,
                "column_count": len(usable_columns),
                "correlations": correlation_records,
                "correlation_matrix": correlation_matrix.to_dict(),
            },
        )

    except Exception:
        if figure is not None:
            _close_figure(figure, plt)
        raise
