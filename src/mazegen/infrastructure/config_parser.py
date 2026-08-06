from pathlib import Path
import sys
from typing import Any, Optional
from .loaders import ConfigLoader, TxtLoader
from .Errors import ConfigError

try:
    from pydantic import BaseModel, model_validator, Field
    from pydantic import field_validator, ConfigDict
    from pydantic import ValidationError
    from enum import Enum
except Exception as e:
    print("Make sure to properly install pydantic")
    print(f"{type(e).__name__}: {e}")
    sys.exit(1)


class AlgorithmEnum(int, Enum):
    """Enumeration of available maze generation algorithms.

    Inherits from `int` to allow direct integer comparison and serialization.

    Attributes:
        DFS (int): Depth-First Search algorithm (0). Generates mazes with long,
            winding corridors and fewer dead ends.
        PRIM (int): Randomized Prim's algorithm (1). Generates mazes with many
            short dead ends and a more uniform, grid-like structure.
    """
    DFS = 0
    PRIM = 1


class ConfigModel(BaseModel):
    """Configuration model for validating maze generator parameters.

    This model manages input validation, aliases for configuration file
    parsing, coordinate tuple conversion, and boundary checks.

    Attributes:
        width (int): Grid width (number of columns). Must be greater than 0.
        height (int): Grid height (number of rows). Must be greater than 0.
        entry (Tuple[int, int]): Entry point coordinates `(x, y)`.
        exit (Tuple[int, int]): Exit point coordinates `(x, y)`.
        output_file (str): Destination path for the generated text maze.
            Must end with `.txt` and contain no whitespaces.
        perfect (bool): Flag indicating if the maze is perfect
        (no loops/isolated areas).
        seed (Optional[int]): Random seed for reproducible maze generation.
        algorithm (AlgorithmEnum): Algorithm choice (DFS or PRIM).
            Defaults to `AlgorithmEnum.DFS`.
        display_mode (Optional[str]): Visualization mode identifier.
    """
    model_config = ConfigDict(populate_by_name=True)
    width: int = Field(..., alias="WIDTH", gt=0, lt=200)
    height: int = Field(..., alias="HEIGHT", gt=0, lt=100)
    entry: tuple[int, int] = Field(..., alias="ENTRY")
    exit: tuple[int, int] = Field(..., alias="EXIT")
    output_file: str = Field(..., alias="OUTPUT_FILE")
    perfect: bool = Field(..., alias="PERFECT")

    seed: Optional[int] = Field(None, alias="SEED")
    algorithm: AlgorithmEnum = Field(AlgorithmEnum.DFS, alias="ALGORITHM")
    display_mode: Optional[str] = Field(None, alias="DISPLAY_MODE")

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coordinates(cls, v: Any) -> object:
        """Parses raw input into a 2D coordinate tuple.
        Args:
            v (Any): Raw input coordinate, expected as a
            string `"x,y"` or a tuple.
        Returns:
            Any: A `(x, y)` integer tuple or raw value if not a string.
        Raises:
            ValueError: If the string format does
            not match `"x,y"` or contains
                non-integer values.
        """
        if isinstance(v, str):
            parts = [c.strip() for c in v.split(",")]
            if len(parts) != 2:
                raise ValueError("Must be a positive format 'x,y'")
            x, y = int(parts[0]), int(parts[1])
            if x < 0 or y < 0:
                raise ValueError("Must be a positive coordinate format 'x,y'")
            return (x, y)
        return v

    @field_validator("algorithm", mode="before", check_fields=False)
    @classmethod
    def parse_algorithm(cls, v: Any) -> Any:
        """Parses and validates the algorithm selector from
        strings or integers.
        Args:
            v (Any): Raw input representation of the algorithm
            name or integer value.
        Returns:
            Any: The corresponding `AlgorithmEnum` member or raw value.
        Raises:
            ValueError: If the string does not match any valid `AlgorithmEnum`.
        """
        if isinstance(v, str):
            name: str = v.strip()
            try:
                return AlgorithmEnum[name.upper()]
            except KeyError:
                pass
            try:
                return int(name)
            except ValueError:
                pass
            valid = ", ".join(m.name.lower() for m in AlgorithmEnum)
            raise ValueError(
                f"Unknown algorithm '{v}'. Valid values: {valid}")
        return v

    @field_validator("output_file")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Ensures the output filename is a valid `.txt` file path.
        Args:
            v (str): Output filename string.
        Returns:
            str: Validated filename string.
        Raises:
            ValueError: If the file does not end with `.txt`
            or contains whitespace.
        """
        if not v.endswith(".txt") or any(
              sep in v for sep in [" ", "\t", "\n"]):
            raise ValueError(
                "Output file must end with .txt and contain no spaces")
        return v

    @model_validator(mode="after")
    def validate_bounds(self) -> "ConfigModel":
        """Verifies that entry and exit coordinates lie within
        the grid boundaries.
        Returns:
            ConfigModel: The validated instance.
        Raises:
            ValueError: If either `entry` or `exit` is out of grid
            bounds `(0 <= x < width, 0 <= y < height)`.
        """
        w, h = self.width, self.height
        for name, pt in [("ENTRY", self.entry), ("EXIT", self.exit)]:
            x, y = pt
            if not (0 <= x < w and 0 <= y < h):
                raise ValueError(
                    f"{name} ({x},{y}) is out of bounds ({w}x{h})")
        return self


class Config:
    """High-level wrapper around `ConfigModel` for configuration management.

    Provides a clean, read-only interface to access validated maze parameters,
    along with factory methods to initialize configuration objects from
    files or inline keyword arguments.
    Args:
        raw_data (dict[str, Any]): Dictionary containing raw
        configuration key-value pairs.
        path (Optional[str]): Path to the source configuration
        file, if applicable.
    Raises:
        ConfigError: If Pydantic validation fails on `raw_data`.
    """

    def __init__(self, raw_data: dict[str, Any],
                 path: Optional[str] = None) -> None:
        self._path: Optional[str] = path
        try:
            self._model = ConfigModel.model_validate(raw_data)
        except ValidationError as e:
            err = e.errors()[0]
            field = ".".join(map(str, err["loc"]))
            print(f"{field}: {err['msg']}")
            sys.exit(1)
        except Exception as e:
            raise ConfigError(f"Configuration error: {e}") from e

    @property
    def path(self) -> Optional[str]:
        """Optional[str]: Path to the loaded configuration file."""
        return self._path

    @property
    def width(self) -> int:
        """int: Maze width in cells."""
        return self._model.width

    @property
    def height(self) -> int:
        """int: Maze height in cells."""
        return self._model.height

    @property
    def entry_pt(self) -> tuple[int, int]:
        """Tuple[int, int]: Entry point (x, y) coordinates."""
        return self._model.entry

    @property
    def exit_pt(self) -> tuple[int, int]:
        """Tuple[int, int]: Exit point (x, y) coordinates."""
        return self._model.exit

    @property
    def output_file(self) -> str:
        """str: Path to the output file where the generated maze
        will be saved."""
        return self._model.output_file

    @property
    def perfect(self) -> bool:
        """bool: Indicates whether the generated maze must be perfect."""
        return self._model.perfect

    @property
    def seed(self) -> Optional[int]:
        """Optional[int]: Random seed for reproducible generation."""
        return self._model.seed

    @property
    def algorithm(self) -> int:
        """int: Integer value corresponding to the selected
        generation algorithm."""
        return self._model.algorithm.value

    @classmethod
    def from_file(
            cls,
            cfg_path: str,
            loader: Optional[ConfigLoader] = None
                ) -> "Config":
        """Creates a `Config` instance by loading settings from a file.
        Args:
            cfg_path (str): Path to the configuration file.
            loader (Optional[ConfigLoader]): Custom loader strategy.
                Defaults to `TxtLoader` if `None`.
        Returns:
            Config: An initialized and validated `Config` instance.
        Raises:
            FileNotFoundError: If `cfg_path` does not exist.
            ConfigError: If content validation fails during parsing.
        """
        if not Path(cfg_path).exists():
            raise FileNotFoundError(f"File {cfg_path} not found.")
        loader = loader if loader is not None else TxtLoader()
        raw_data = loader.load(cfg_path)
        return cls(raw_data, path=cfg_path)

    @classmethod
    def from_params(cls, **kwargs: Any) -> "Config":
        """Creates a `Config` instance directly from keyword arguments.
        Args:
            **kwargs (Any): Configuration fields such as `width`, `height`,
                `entry`, `exit`, `output_file`, `perfect`, etc.
        Returns:
            Config: An initialized and validated `Config` instance.
        Raises:
            ConfigError: If keyword arguments fail configuration validation.
        """
        return cls(kwargs, path=None)
