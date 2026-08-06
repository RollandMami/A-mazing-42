from abc import ABC, abstractmethod
from typing import List, Tuple, Optional


class BaseSolver(ABC):
    """Abstract base class defining the interface for maze solvers.

    This class enforces a consistent API across different pathfinding
    algorithms (e.g., BFS, DFS, A*).
    """

    @abstractmethod
    def solve(self, grid: List[List[int]],
              start: Tuple[int, int],
              end: Tuple[int, int]
              ) -> Optional[tuple[List[Tuple[int, int]], str]]:
        """Solves the maze grid from the start coordinate to
        the end coordinate.

        Args:
            grid (List[List[int]]): Two-dimensional list representing the maze
                structure, where integer bitmasks indicate
                cell wall directions.
            start (Tuple[int, int]): Initial (x, y) coordinate
            pair representing
                the entry point.
            end (Tuple[int, int]): Target (x, y) coordinate pair representing
                the exit point.

        Returns:
            Optional[Tuple[List[Tuple[int, int]], str]]: A tuple containing:
                - List[Tuple[int, int]]: The ordered list of (x, y) coordinates
                forming the path from start to end.
                - str: The solver or algorithm name / execution metadata.
                Returns `None` if no valid path exists between start and end.

        Raises:
            NotImplementedError: If the subclass does not
            implement this method.
        """
        ...
