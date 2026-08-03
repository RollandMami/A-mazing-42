from abc import ABC, abstractmethod
from typing import List, Tuple, Optional


class BaseSolver(ABC):
    """Abstract interface for structurin solver."""

    @abstractmethod
    def solve(self, grid: List[List[int]],
              start: Tuple[int, int],
              end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Resolve the labyrinthe and retur the list of path (liste de cases)
        from start to end, and None is returned if no solution.
        """
        ...
