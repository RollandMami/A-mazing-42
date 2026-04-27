from infrastructure import Config, BaseWriter
import random
from typing import List, Tuple, Set
from generator.Errors import GenerationError
from generator.base_gen import BaseGen


class PrimGenerator(BaseGen):
    def generate(self) -> None:
        """
        Generates a maze using Prim's algorithm and adds 
        imperfections if the maze is not set to be perfect.
        """
        random.seed(self.seed)
        # 1. Start with a random cell
        start_x: int = random.randint(0, self.width - 1)
        start_y: int = random.randint(0, self.height - 1)
        visited: set[Tuple[int, int]] = set()
        visited.add((start_x, start_y))
        frontiers: List[Tuple[int, int]] = []
        # Helper to add initial neighbors to frontiers
        self._add_to_frontiers(start_x, start_y, visited, frontiers)
        while frontiers:
            # 2. Pick a random frontier cell
            current_cell: Tuple[int, int] = random.choice(frontiers)
            curr_x, curr_y = current_cell
            frontiers.remove(current_cell)
            # 3. Find neighbors of this frontier that are already in the maze
            potential_connections: List[Tuple[int, int, str, int]] = []
            for direction_name, (dx, dy, bit_idx) in self.direction.items():
                nx: int = curr_x + dx
                ny: int = curr_y + dy
                if (nx, ny) in visited:
                    potential_connections.append((nx, ny, direction_name, bit_idx))
            if potential_connections:
                # 4. Connect the frontier to the maze
                conn_x, conn_y, dir_name, bit_idx = random.choice(potential_connections)
                # Remove wall on the current frontier cell
                wall_value: int = 2 ** bit_idx
                self.maze[curr_y][curr_x] -= wall_value
                # Remove the opposite wall on the already visited cell
                opposites: dict[str, str] = {"N": "S", "S": "N", "E": "O", "O": "E"}
                opp_dir_name: str = opposites[dir_name]
                opp_bit_idx: int = self.direction[opp_dir_name][2]
                opp_wall_value: int = 2 ** opp_bit_idx
                self.maze[conn_y][conn_x] -= opp_wall_value
                # 5. Mark as visited and expand frontiers
                visited.add((curr_x, curr_y))
                self._add_to_frontiers(curr_x, curr_y, visited, frontiers)
        # 6. Add loops if the maze is not perfect
        if not self._perfect:
            self._make_imperfection()

    def _add_to_frontiers(self, x: int, y: int, visited: set, frontiers: List[Tuple[int, int]]) -> None:
        """Adds unvisited neighbors to the frontiers list."""
        for _, (dx, dy, _) in self.direction.items():
            nx: int = x + dx
            ny: int = y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if (nx, ny) not in visited and (nx, ny) not in frontiers:
                    # Check if the cell is not part of the 42 mask
                    if self._mask_42 is None or (nx, ny) not in self._mask_42:
                        frontiers.append((nx, ny))
