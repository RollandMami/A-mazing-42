from abc import ABC, abstractmethod
from typing import List, Tuple, Optional


class BaseSolver(ABC):
    """Interface abstraite pour un solveur de labyrinthe."""

    @abstractmethod
    def solve(self, grid: List[List[int]],
              start: Tuple[int, int],
              end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Resout le labyrinthe et retourne le chemin (liste de cases)
        de start a end, ou None si aucun chemin n'existe.
        """
        ...
