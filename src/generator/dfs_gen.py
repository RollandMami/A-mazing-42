from infrastructure import Config, BaseWriter
import random
from typing import List, Tuple, Set
from generator.Errors import GenerationError
from generator.base_gen import BaseGen


class DfsGenerator(BaseGen):
    def __init__(self, cfg: Config, writer: BaseWriter) -> None:
        super().__init__(cfg, writer)

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
            if self._mask_42:
                for point in self._mask_42:
                    visited.add(point)
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
