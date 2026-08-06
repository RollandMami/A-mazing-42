from ..infrastructure import Config, BaseWriter
import random
from typing import List, Tuple, Set, Any
from .Errors import GenerationError
from .base_gen import BaseGen


class DfsGenerator(BaseGen):
    """Maze generator utilizing the Randomized
    Depth-First Search (DFS) algorithm.

    This generator produces perfect mazes (or
    imperfect mazes if configured via
    `BaseGen`) using a stack-based recursive
    backtracker approach. It handles grid
    boundaries, seed-based randomization,
    entrance setting, and respects masked cells
    (such as the '42' logo).
    """
    def __init__(self, cfg: Config, writer: BaseWriter) -> None:
        """Initializes the DFS maze generator
        with configuration and writer instances.

        Args:
            cfg: Configuration object specifying
            dimensions, entry/exit coordinates,
                random seed, and output preferences.
            writer: Output writer responsible for
            exporting the generated maze data.
        """
        super().__init__(cfg, writer)

    def generate(self) -> None:
        """Generates the maze structure using the DFS
        recursive backtracker algorithm.

        Initializes the grid with all walls present,
        carves paths starting from the
        entry point, skips masked coordinates, and
        calls `_finalize()` upon completion.

        Raises:
            GenerationError: If maze dimensions are
            non-positive or if an unexpected
            error occurs during the generation procedure.
        """
        try:
            self.maze = [
                [15 for _ in range(self._width)]
                for _ in range(self._height)
            ]
            if self.width <= 0 or self.height <= 0:
                raise GenerationError("Dimension must be positive.")
            random.seed(self.seed)
            if not self._entry:
                self._entry = (0, 0)
            start_node: Tuple[int, int] = self._entry
            stack: List[Tuple[int, int]] = [start_node]
            visited: Set[Tuple[int, int]] = {start_node}
            if self._mask_42:
                for point in self._mask_42:
                    visited.add(point)
            while stack:
                curr_x, curr_y = stack[-1]
                voisin: list[Any] = self._get_voisin(curr_x, curr_y, visited)
                if voisin:
                    next_x, next_y, bit_index, direction = random.choice(
                        voisin
                    )
                    self._break_wall(
                        curr_x, curr_y,
                        next_x, next_y,
                        bit_index
                    )
                    # deplacement
                    visited.add((next_x, next_y))
                    stack.append((next_x, next_y))
                else:
                    stack.pop()
            self._finalize()
        except Exception as e:
            raise GenerationError(f"Generation failed : {e}")

    def _get_voisin(self, curr_x: int, curr_y: int, visited: set[Any]
                    ) -> list[tuple[int, int, int, str]]:
        """Retrieves unvisited valid neighboring cells
        around the given coordinates.

        Args:
            curr_x: Current column coordinate.
            curr_y: Current row coordinate.
            visited: Set of coordinate tuples `(x, y)`
            already processed or masked.

        Returns:
            A list of tuples representing valid neighbors. Each tuple contains:
                - int: Neighbor column index (`nx`).
                - int: Neighbor row index (`ny`).
                - int: Wall bit index corresponding to the direction.
                - str: Direction key ("N", "E", "S", or "O").
        """
        voisin: list[tuple[int, int, int, str]] = []
        for direction, (dx, dy, bit_index) in self.direction.items():
            nx, ny = curr_x + dx, curr_y + dy
            if (
                0 <= nx < self.width
                and 0 <= ny < self.height
                and (nx, ny) not in visited
            ):
                voisin.append((nx, ny, bit_index, direction))
        return voisin

    def _break_wall(self, cx: int, cy: int, next_x: int,
                    next_y: int, bit_index: int
                    ) -> None:
        """Removes the shared wall between the current
        cell and a target neighbor cell.

        Updates the bitwise integer representations
        of both cells in the `maze` grid.

        Args:
            cx: Current cell column coordinate.
            cy: Current cell row coordinate.
            next_x: Target neighbor column coordinate.
            next_y: Target neighbor row coordinate.
            bit_index: Index of the wall bit to carve on the current cell.
        """
        poids: int = 2 ** bit_index
        self.maze[cy][cx] -= poids
        # la mur opposée chez le voisin
        bit_opose: int = (bit_index + 2) % 4
        poids_voisin: int = 2 ** bit_opose
        self.maze[next_y][next_x] -= poids_voisin
