from infrastructure import Config
import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Set
# Algorithme Recursive Backtracker


class MazeError(Exception):
    """Classe de base pour les erreurs du projet"""
    pass


class GenerationError(MazeError):
    """Erreur spécifique à l'algorithme de génération"""
    pass


class BaseWriter(ABC):
    @abstractmethod
    def write(self, maze: List[List[int]], destination: str) -> None:
        """Méthode pour écrire le labyrinthe sur un support donné"""
        pass


class TxtWriter(BaseWriter):
    def write(self, maze: List[List[int]], destination: str) -> None:
        try:
            with open(destination, 'w') as f:
                for row in maze:
                    line = "".join(format(cell, 'X') for cell in row)
                    f.write(line + "\n")
            print(f"Succès : Labyrinthe exporté dans {destination}")
        except IOError as e:
            print(f"Erreur lors de l'écriture du fichier : {e}")


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
        self.maze: list[int] = [
            [15 for _ in range(self._height)] for _ in range(self._width)
        ]
        self._direction: dict[str, tuple] = {
            "N": (0, -1, 0),
            "E": (1, 0, 1),
            "S": (0, 1, 2),
            "O": (-1, 0, 3)
        }
        self._writer = writer if writer else TxtWriter()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @abstractmethod
    def generate(self) -> None:
        pass

    def export(self) -> None:
        self._writer.write(self.maze, self.output_file)


class Dfs_generator(Base_Gen):
    def __init__(self, cfg: Config, writer: BaseWriter) -> None:
        super().__init__(cfg, writer)

    @property
    def seed(self):
        return self._seed

    @property
    def direction(self):
        return self._direction

    def generate(self) -> None:
        try:
            if self.width <= 0 or self.height <= 0:
                raise GenerationError("La largeur doit être positive.")
            random.seed(self.seed)
            if not self._entry:
                self._entry = (0, 0)
            start_node: Tuple[int, int] = self._entry
            stack: List[Tuple[int, int]] = [start_node]
            visited: Set[Tuple[int, int]] = {start_node}
            while stack:
                curr_x, curr_y = stack[-1]
                voisin: list = self._get_voisin(curr_x, curr_y, visited)
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
        except Exception as e:
            raise GenerationError(f"Échec de la génération : {e}")

    def _get_voisin(self, curr_x: int, curr_y: int, visited: set) -> list:
        voisin: list = []
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
        poids: int = 2 ** bit_index
        self.maze[cy][cx] -= poids
        # la mur opposée chez le voisin
        bit_opose: int = (bit_index + 2) % 4
        poids_voisin: int = 2 ** bit_opose
        self.maze[next_y][next_x] -= poids_voisin
