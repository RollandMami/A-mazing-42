from collections import deque
from typing import List, Tuple, Optional
from .base_solver import BaseSolver


class BfsSolver(BaseSolver):
    """
    Solveur BFS (Breadth-First Search) pour trouver le plus court chemin
    dans un labyrinthe represente par une grille de murs codes en bits.

    Chaque cellule contient un entier dont les bits indiquent les murs :
      Bit 0 (0x1) = Nord
      Bit 1 (0x2) = Est
      Bit 2 (0x4) = Sud
      Bit 3 (0x8) = Ouest
    Un mur est present si le bit correspondant est a 1.
    """

    # Directions : (dx, dy)
    DIRECTIONS = [
        (0, -1),  # Nord
        (1,  0),  # Est
        (0,  1),  # Sud
        (-1, 0),  # Ouest
    ]

    DIRECTIONS_Dict = {
        (0, -1): 'N',
        (1,  0): 'E',
        (0,  1): 'S',
        (-1, 0): 'W'
    }

    # Mur bit pour chaque direction depuis la cellule courante
    WALL_BITS = {
        (0, -1): 0x1,  # Nord
        (1,  0): 0x2,  # Est
        (0,  1): 0x4,  # Sud
        (-1, 0): 0x8,  # Ouest
    }

    # Mur oppose dans la cellule voisine
    OPPOSITE_BITS = {
        (0, -1): 0x4,  # Nord -> oppose Sud dans la cellule au Nord
        (1,  0): 0x8,  # Est  -> oppose Ouest dans la cellule a l'Est
        (0,  1): 0x1,  # Sud  -> oppose Nord dans la cellule au Sud
        (-1, 0): 0x2,  # Ouest-> oppose Est dans la cellule a l'Ouest
    }

    def solve(self, grid: List[List[int]],
              start: Tuple[int, int],
              end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Resout le labyrinthe par BFS et retourne le chemin le plus court."""
        if not grid or not grid[0]:
            return None

        height = len(grid)
        width = len(grid[0])

        # Verifier que start et end sont dans la grille
        sx, sy = start
        ex, ey = end
        if not (0 <= sx < width and 0 <= sy < height):
            return None
        if not (0 <= ex < width and 0 <= ey < height):
            return None

        # BFS
        visited = [[False] * width for _ in range(height)]
        # parent[x][y] = (px, py) pour reconstruire le chemin
        parent: List[List[Tuple[int, int]]] = [
            [(-1, -1)] * width for _ in range(height)]

        queue: deque[Tuple[int, int]] = deque()
        queue.append(start)
        visited[sy][sx] = True

        while queue:
            cx, cy = queue.popleft()

            # Arrive a la sortie ?
            if (cx, cy) == (ex, ey):
                # Reconstruire le chemin
                path: List[Tuple[int, int]] = []
                literal: str = ""
                x, y = cx, cy
                while (x, y) != (-1, -1):
                    path.append((x, y))
                    px, py = parent[y][x]
                    if (px, py) != (-1, -1):
                        dx, dy = x - px, y - py
                        l: str = self.DIRECTIONS_Dict[(dx, dy)]
                        literal += l
                    x, y = px, py
                path.reverse()
                return path, literal

            cell = grid[cy][cx]

            # Explorer les 4 directions
            for dx, dy in self.DIRECTIONS:
                nx, ny = cx + dx, cy + dy

                # Verifier les limites
                if not (0 <= nx < width and 0 <= ny < height):
                    continue

                # Deja visite ?
                if visited[ny][nx]:
                    continue

                # Verifier qu'il n'y a pas de mur dans cette direction
                wall_bit = self.WALL_BITS[(dx, dy)]
                if cell & wall_bit:
                    continue  # mur present, on ne peut pas passer

                # Verifier que la cellule voisine n'a pas de mur oppose
                neighbor_cell = grid[ny][nx]
                opp_bit = self.OPPOSITE_BITS[(dx, dy)]
                if neighbor_cell & opp_bit:
                    continue

                visited[ny][nx] = True
                parent[ny][nx] = (cx, cy)
                queue.append((nx, ny))

        # Aucun chemin trouve
        return None
