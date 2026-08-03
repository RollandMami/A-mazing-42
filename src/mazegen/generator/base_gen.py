from ..infrastructure import Config, BaseWriter, TxtWriter
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from ..solver import BaseSolver, BfsSolver
import random


class BaseGen(ABC):
    def __init__(self,
                 cfg: Config,
                 writer: BaseWriter,
                 solver: BaseSolver = BfsSolver
                 ) -> None:
        # dimension du maze:
        self._width: int = cfg.width
        self._height: int = cfg.height
        # entree et sortie:
        self._entry: tuple[int, int] = cfg.entry_pt
        self._exit: tuple[int, int] = cfg.exit_pt
        # le fichier ou ecrire:
        self.output_file: str = cfg.output_file
        self._perfect: bool = cfg.perfect
        self._seed: int | None = cfg.seed
        self.maze: List[List[int]] = [
            [15 for _ in range(self._width)] for _ in range(self._height)
        ]
        self._direction: dict[str, tuple[int, ...]] = {
            "N": (0, -1, 0),
            "E": (1, 0, 1),
            "S": (0, 1, 2),
            "O": (-1, 0, 3)
        }
        self.solver: BaseSolver = solver()
        self._size: int = self._height * self._width
        self._min_logo_size: int = 12 * 8
        self._writer = writer if writer else TxtWriter()
        self._mask_42: Optional[list[tuple[int, int]]] = None
        if self._seed is None:
            self._seed = random.randint(0, 999)
        if self._size >= self._min_logo_size:
            self._mask_42 = self._apply_mask()
        else:
            print("The maze dimension is too small for 42 logo")

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def seed(self) -> int | None:
        return self._seed

    @property
    def direction(self) -> dict[str, tuple[int, ...]]:
        return self._direction

    @abstractmethod
    def generate(self) -> None:
        pass

    def export(self) -> None:
        self._writer.write(self.maze, self.output_file)
        meta: str = f"\n{self._entry}\n{self._exit}"
        self._writer.insert(meta, self.output_file)
        res = self.solver.solve(self.maze, self._entry, self._exit)[1]
        solution: str = f"\n{res}"
        self._writer.insert(solution, self.output_file)

    def _apply_mask(self) -> List[Tuple[int, int]]:
        coords: List[Tuple[int, int]] = [
            # 4
            (-3, -2), (-3, -1), (-3, 0), (-2, 0),
            (-1, 0), (-1, 1), (-1, 2),
            # 2
            (1, -2), (2, -2), (3, -2), (3, -1),
            (3, 0), (2, 0), (1, 0), (1, 1),
            (1, 2), (2, 2), (3, 2)
        ]
        middle_x: int = self.width // 2
        middle_y: int = self.height // 2
        return [
            (point[0] + middle_x, point[1] + middle_y) for point in coords
            ]

    def _make_imperfection(self) -> None:
        """Randomly removes walls to create cycles/loops in the maze."""
        # We break about 10% of the total potential internal walls
        walls_to_break: int = int(self.width * self.height * 0.1)
        # Map for opposite directions
        opposites: dict[str, str] = {"N": "S", "S": "N", "E": "O", "O": "E"}
        for _ in range(walls_to_break):
            # Pick a random cell (excluding borders to simplify)
            rx: int = random.randint(1, self.width - 2)
            ry: int = random.randint(1, self.height - 2)
            # Ne pas casser les murs des cellules du motif 42
            if self._mask_42 is not None and (rx, ry) in self._mask_42:
                continue
            # Pick a random direction
            dir_name: str = random.choice(list(self.direction.keys()))
            dx, dy, bit_idx = self.direction[dir_name]
            nx: int = rx + dx
            ny: int = ry + dy
            # Ne pas casser les murs qui font face au motif 42
            if self._mask_42 is not None and (nx, ny) in self._mask_42:
                continue
            # Power of 2 for the wall
            power: int = 2 ** bit_idx
            # If the wall exists (value // power) % 2 == 1
            if (self.maze[ry][rx] // power) % 2 == 1:
                # Remove wall on current cell
                self.maze[ry][rx] -= power
                # Remove wall on neighbor cell
                opp_dir: str = opposites[dir_name]
                opp_bit: int = self.direction[opp_dir][2]
                self.maze[ny][nx] -= (2 ** opp_bit)
