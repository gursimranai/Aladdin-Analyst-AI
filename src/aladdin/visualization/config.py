from dataclasses import dataclass
from pathlib import Path


@dataclass
class VisualizationConfig:
    """Configuration options for chart generation."""

    width: float = 10.0
    height: float = 6.0
    dpi: int = 100
    output_format: str = "png"
    show: bool = False
    save: bool = False
    output_dir: Path | None = None

    def __post_init__(self) -> None:
        """Validate visualization configuration."""

        if isinstance(self.width, bool) or not isinstance(self.width, (int, float)):
            raise TypeError("width must be a number.")

        if isinstance(self.height, bool) or not isinstance(self.height, (int, float)):
            raise TypeError("height must be a number.")

        if self.width <= 0:
            raise ValueError("width must be greater than zero.")

        if self.height <= 0:
            raise ValueError("height must be greater than zero.")

        if isinstance(self.dpi, bool) or not isinstance(self.dpi, int):
            raise TypeError("dpi must be an integer.")

        if self.dpi <= 0:
            raise ValueError("dpi must be greater than zero.")

        if not isinstance(self.output_format, str):
            raise TypeError("output_format must be a string.")

        self.output_format = self.output_format.lower().strip()

        if self.output_format not in {"png", "jpg", "jpeg", "svg", "pdf"}:
            raise ValueError("Unsupported output format.")

        if not isinstance(self.show, bool):
            raise TypeError("show must be a boolean.")

        if not isinstance(self.save, bool):
            raise TypeError("save must be a boolean.")

        if self.output_dir is not None:
            if not isinstance(self.output_dir, (str, Path)):
                raise TypeError("output_dir must be a string or Path.")

            self.output_dir = Path(self.output_dir)

        if self.save and self.output_dir is None:
            raise ValueError("output_dir must be provided when save is enabled.")
