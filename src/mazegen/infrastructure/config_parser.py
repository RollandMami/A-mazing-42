from pathlib import Path
import sys
from typing import Any, Optional
from .loaders import ConfigLoader, TxtLoader
from .Errors import ConfigError

try:
    from pydantic import BaseModel, model_validator, Field
    from pydantic import field_validator
    from enum import Enum
except Exception as e:
    print("Make sure to properly install pydantic")
    print(f"{type(e).__name__}: {e}")
    sys.exit(1)


class AlgorithmEnum(int, Enum):
    DFS = 1
    PRIM = 2
    ASTAR = 3


class ConfigModel(BaseModel):
    width: int = Field(..., alias="WIDTH", gt=0)
    height: int = Field(..., alias="HEIGHT", gt=0)
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
        if isinstance(v, str):
            parts = [c.strip() for c in v.split(",")]
            if len(parts) != 2:
                raise ValueError("Must be a coordinate format 'x,y'")
            return (int(parts[0]), int(parts[1]))
        return v

    @field_validator("algorithm", mode="before", check_fields=False)
    @classmethod
    def parse_algorithm(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                pass
        return v

    @field_validator("output_file")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        if not v.endswith(".txt") or any(
              sep in v for sep in [" ", "\t", "\n"]):
            raise ValueError("Output file must end with",
                             " .txt and contain no spaces")
        return v

    @model_validator(mode="after")
    def validate_bounds(self) -> "ConfigModel":
        w, h = self.width, self.height
        for name, pt in [("ENTRY", self.entry), ("EXIT", self.exit)]:
            x, y = pt
            if not (0 <= x < w and 0 <= y < h):
                raise ValueError(
                    f"{name} ({x},{y}) is out of bounds ({w}x{h})")
        return self


class Config:
    """This class is used for gather configuration info
    needed by the Generator class"""

    def __init__(
            self,
            cfg_path: str,
            loader: ConfigLoader = TxtLoader()
                ) -> None:
        self._path: str = cfg_path
        if not Path(cfg_path).exists():
            raise FileNotFoundError(f"File {cfg_path} not found.")
        raw_data = loader.load(cfg_path)
        try:
            self._model = ConfigModel.model_validate(raw_data)
        except Exception as e:
            raise ConfigError(f"Configuration error: {e}") from e

    @property
    def path(self) -> str: return self._path
    @property
    def width(self) -> int: return self._model.width
    @property
    def height(self) -> int: return self._model.height
    @property
    def entry_pt(self) -> tuple[int, int]: return self._model.entry
    @property
    def exit_pt(self) -> tuple[int, int]: return self._model.exit
    @property
    def output_file(self) -> str: return self._model.output_file
    @property
    def perfect(self) -> bool: return self._model.perfect
    @property
    def seed(self) -> Optional[int]: return self._model.seed
    @property
    def algorithm(self) -> int: return self._model.algorithm.value
