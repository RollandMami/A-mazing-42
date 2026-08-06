import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Protocol
from ..solver import BfsSolver
from ..infrastructure import Config, BaseWriter, TxtWriter


class Solver(Protocol):
    """Protocol defining the interface for maze solving algorithms.

    Classes implementing this protocol must provide a mechanism to find a path
    through a grid-based maze from a starting point to an endpoint.
    """
    def solve(self, grid: List[List[int]],
              start: Tuple[int, int],
              end: Tuple[int, int]
              ) -> Optional[tuple[List[Tuple[int, int]], str]]:
        """Solves the maze for a given grid, start, and end positions.

        Args:
            grid: A 2D list of integers representing the maze
            structure where each cell value contains wall
            data (bitwise representation).
            start: A tuple of (column, row) representing the
            starting coordinates.
            end: A tuple of (column, row) representing the target
            destination coordinates.

        Returns:
            A tuple containing:
                - List[Tuple[int, int]]: The path from start to end
                as a list of (column, row) coordinate tuples.
                - str: A string representing the directions
                or metadata of the path.
            Returns None if no valid path exists between start and end.
        """
        ...


class BaseGen(ABC):
    """Abstract base class for maze generators.

    Provides common functionality for initializing maze grids, handling
    configurations, applying masks (such as the 42 logo), introducing
    imperfections (loops), solving, and exporting the generated maze.

    Attributes:
        output_file (str): Path to the destination file where
        the maze is exported.
        maze (List[List[int]]): 2D grid representing the maze.
        Each cell value is a bitwise integer representation of its walls.
    """
    def __init__(self,
                 cfg: Config,
                 writer: BaseWriter,
                 solver: Solver = BfsSolver()
                 ) -> None:
        """Initializes the maze generator with
        configuration, writer, and solver.

        Args:
            cfg: Configuration object containing dimensions, entry/exit points,
                seed, and target output path.
            writer: File writer instance responsible for exporting maze data.
            solver: Algorithm solver implementation used to
            resolve the maze path.
        """
        self._width: int = cfg.width
        self._height: int = cfg.height
        self._entry: tuple[int, int] = cfg.entry_pt
        self._exit: tuple[int, int] = cfg.exit_pt
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
        self._size: int = self._height * self._width
        self._min_logo_size: int = 12 * 8
        self._writer = writer if writer else TxtWriter()
        self._solver = solver
        self._mask_42: Optional[list[tuple[int, int]]] = None
        if self._seed is None:
            self._seed = random.randint(0, 999)
        if self._size >= self._min_logo_size:
            self._mask_42 = self._apply_mask()
        else:
            print("The maze dimension is too small for 42 logo")
        self._solution: Optional[tuple[List[Tuple[int, int]], str]] = None
        self._generated: bool = False

    def _finalize(self) -> None:
        """Finalizes the generation process.

        Applies imperfections if the maze is not configured to be perfect,
        marks the maze as generated, and resets cached solutions.
        Must be called by subclasses at the end of their `generate()` method.
        """
        if self._perfect is False:
            self._make_imperfection()
        self._generated = True
        self._solution = None

    def export(self) -> None:
        """Exports the generated maze, its metadata,
        and solution to the output file.

        Raises:
            RuntimeError: If called before `generate()`
            or if no valid path exists
                between the entry and exit points.
        """
        if not self._generated:
            raise RuntimeError(
                "Cannot export before generate() has been called"
            )
        self._writer.write(self.maze, self.output_file)
        meta: str = f"\n{self._entry}\n{self._exit}"
        self._writer.insert(meta, self.output_file)
        solution = self.solution
        if solution is None:
            raise RuntimeError(
                "Maze has no valid solution between entry and exit"
            )
        res = solution[1]
        solution_str: str = f"\n{res}"
        self._writer.insert(solution_str, self.output_file)

    def _apply_mask(self) -> List[Tuple[int, int]]:
        """Calculates coordinates for the central '42' logo mask.

        Returns:
            List[Tuple[int, int]]: Coordinates offset
            to center the '42' pattern
            within the maze dimensions.
        """
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
        """Randomly removes internal walls to create loops
        in non-perfect mazes.

        Removes approximately 10% of potential internal walls while explicitly
        preserving walls around cells that form part of the '42' logo mask.
        """
        # We break about 10% of the total potential internal walls
        walls_to_break: int = int(self.width * self.height * 0.1)
        # Map for opposite directions
        opposites: dict[str, str] = {"N": "S", "S": "N", "E": "O", "O": "E"}
        for _ in range(walls_to_break):
            # Pick a random cell (excluding borders to simplify)
            rx: int = random.randint(1, self.width - 2)
            ry: int = random.randint(1, self.height - 2)
            # do not break wall face to 42 mask
            if self._mask_42 is not None and (rx, ry) in self._mask_42:
                continue
            # Pick a random direction
            dir_name: str = random.choice(list(self.direction.keys()))
            dx, dy, bit_idx = self.direction[dir_name]
            nx: int = rx + dx
            ny: int = ry + dy
            # do not break wall face to 42 mask
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

    @property
    def entry(self) -> tuple[int, int]:
        """tuple[int, int]: Coordinates (column, row) of the maze entrance."""
        return self._entry

    @property
    def exit(self) -> tuple[int, int]:
        """tuple[int, int]: Coordinates (column, row) of the maze exit."""
        return self._exit

    @property
    def mask_42(self) -> list[tuple[int, int]] | None:
        """Optional[list[tuple[int, int]]]: Coordinates of the '42'
        logo cells, if applied."""
        return self._mask_42

    @property
    def width(self) -> int:
        """int: Width (number of columns) of the maze."""
        return self._width

    @property
    def height(self) -> int:
        """int: Height (number of rows) of the maze."""
        return self._height

    @property
    def seed(self) -> int | None:
        """Optional[int]: Random seed used for maze generation."""
        return self._seed

    @property
    def direction(self) -> dict[str, tuple[int, ...]]:
        """dict[str, tuple[int, ...]]: Mapping of direction
        names to offsets and bit indices."""
        return self._direction

    @property
    def solution(self) -> Optional[tuple[List[Tuple[int, int]], str]]:
        """Optional[tuple[List[Tuple[int, int]], str]]:
        Solved path and directional metadata.

        Calculates and caches the solution lazily upon access.

        Raises:
            RuntimeError: If accessed before `generate()` has been called.
        """
        if not self._generated:
            raise RuntimeError(
                "Cannot access solution before generate() has been called"
            )
        if self._solution is None:
            self._solution = self._solver.solve(
                self.maze, self._entry, self._exit)
        return self._solution

    @abstractmethod
    def generate(self) -> None:
        """Generates the maze structure.

        Subclasses must implement this method and call
        `_finalize()` at the end.
        """
        ...
