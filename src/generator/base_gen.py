from infrastructure import Config, BaseWriter, TxtWriter
from abc import ABC, abstractmethod
from typing import List, Tuple
import random


class Base_Gen(ABC):
    def __init__(self, cfg: Config, writer: BaseWriter) -> None:
        # dimension du maze:
        self._width: int = cfg.width
        self._height: int = cfg.height
        # entree et sortie:
        self._entry: tuple = cfg.entry_pt
        self._exit: tuple = cfg.exit_pt
        # le fichier ou ecrire:
        self.output_file: str = cfg.output_file
        self._perfect: bool = cfg.perfect
        self._seed: int = cfg.seed
        self.maze: List[List[int]] = [
            [15 for _ in range(self._width)] for _ in range(self._height)
        ]
        self._direction: dict[str, tuple] = {
            "N": (0, -1, 0),
            "E": (1, 0, 1),
            "S": (0, 1, 2),
            "O": (-1, 0, 3)
        }
        self._size: int = self._height * self._width
        self._min_logo_size: int = 12 * 8
        self._writer = writer if writer else TxtWriter()
        self._mask_42: list = None
        if self._seed is None:
            self._seed = random.randint(0, 999)
        if self._size >= self._min_logo_size:
            self._mask_42 = self._apply_mask()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def seed(self):
        return self._seed

    @property
    def direction(self):
        return self._direction

    @abstractmethod
    def generate(self) -> None:
        pass

    def export(self) -> None:
        self._writer.write(self.maze, self.output_file)
        self._writer.write("\n", self.output_file)
        self._writer.write(self._entry, self.output_file)
        self._writer.write(self._exit, self.output_file)

    def _apply_mask(self) -> List[Tuple[int, int]]:
        coords: List[Tuple[int, int]] = [
            # 4
            (-3, -2), (-3, -1), (-3, 0), (-2, 0),
            (-1, 0), (-1, 1), (-1, 2),
            # 2
            (1, -2), (2, -2), (3, -2), (3, -1),
            (3, 0), (2, 0), (1, 0), (1, 1), (1, 2),
            (1, 3), (2, 3), (3, 3)
        ]
        middle_x: int = self.width // 2
        middle_y: int = self.height // 2
        return [
            (point[0] + middle_x, point[1] + middle_y) for point in coords
            ]
