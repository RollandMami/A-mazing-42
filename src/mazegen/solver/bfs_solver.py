from collections import deque
from typing import List, Tuple, Optional
from .base_solver import BaseSolver


class BfsSolver(BaseSolver):
    """Breadth-First Search (BFS) maze solver.

    This class implements the BFS algorithm to find the guaranteed shortest
    path in a maze represented by a 2D grid of bitmask-encoded walls.

    Attributes:
        DIRECTIONS (List[Tuple[int, int]]): Directional vectors for North,
            East, South, and West navigation.
        DIRECTIONS_Dict (Dict[Tuple[int, int], str]): Mapping of directional
            vectors to their cardinal letter representation
            ('N', 'E', 'S', 'W').
        WALL_BITS (Dict[Tuple[int, int], int]): Bitmask values corresponding to
            walls in each direction from the current cell.
        OPPOSITE_BITS (Dict[Tuple[int, int], int]): Bitmask values
        corresponding
            to walls on the adjacent side of target neighboring cells.
    """

    DIRECTIONS = [
        (0, -1),  # North
        (1,  0),  # East
        (0,  1),  # South
        (-1, 0),  # West
    ]

    DIRECTIONS_Dict = {
        (0, -1): 'N',
        (1,  0): 'E',
        (0,  1): 'S',
        (-1, 0): 'W'
    }

    WALL_BITS = {
        (0, -1): 0x1,  # North
        (1,  0): 0x2,  # East
        (0,  1): 0x4,  # South
        (-1, 0): 0x8,  # West
    }

    OPPOSITE_BITS = {
        (0, -1): 0x4,  # North -> South wall in neighbor
        (1,  0): 0x8,  # East  -> West wall in neighbor
        (0,  1): 0x1,  # South -> North wall in neighbor
        (-1, 0): 0x2,  # West  -> East wall in neighbor
    }

    def solve(self, grid: List[List[int]],
              start: Tuple[int, int],
              end: Tuple[int, int]
              ) -> Optional[tuple[List[Tuple[int, int]], str]]:
        """Solves the maze grid using Breadth-First Search (BFS).

        Args:
            grid (List[List[int]]): 2D grid representing the maze structure,
                where each integer cell contains a 4-bit wall bitmask.
            start (Tuple[int, int]): Starting (x, y) coordinates.
            end (Tuple[int, int]): Target (x, y) coordinates.

        Returns:
            Optional[Tuple[List[Tuple[int, int]], str]]: A tuple containing:
                - List[Tuple[int, int]]: The sequence of (x, y) cell
                coordinates
                  representing the shortest path from start to end.
                - str: A string of cardinal directions ('N', 'S', 'E', 'W')
                  describing the movements taken along the path.
                Returns `None` if no path is found or input coordinates are
                out of bounds.
        """
        if not grid or not grid[0]:
            return None

        height = len(grid)
        width = len(grid[0])

        # Verify that start & end are in the maze
        sx, sy = start
        ex, ey = end
        if not (0 <= sx < width and 0 <= sy < height):
            return None
        if not (0 <= ex < width and 0 <= ey < height):
            return None

        # BFS
        visited = [[False] * width for _ in range(height)]
        # parent[x][y] = (px, py) for path
        parent: List[List[Tuple[int, int]]] = [
            [(-1, -1)] * width for _ in range(height)]

        queue: deque[Tuple[int, int]] = deque()
        queue.append(start)
        visited[sy][sx] = True

        while queue:
            cx, cy = queue.popleft()

            # exit ?
            if (cx, cy) == (ex, ey):
                # Reconstruct path
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
                literal = literal[::-1]
                return path, literal

            cell = grid[cy][cx]

            # Explorer les 4 directions
            for dx, dy in self.DIRECTIONS:
                nx, ny = cx + dx, cy + dy

                # bound verification
                if not (0 <= nx < width and 0 <= ny < height):
                    continue

                # already visited ?
                if visited[ny][nx]:
                    continue

                # verify that there's no wall on this direction
                wall_bit = self.WALL_BITS[(dx, dy)]
                if cell & wall_bit:
                    continue  # if wall, we cant go further

                # verify that the opposite cell does not have wall
                neighbor_cell = grid[ny][nx]
                opp_bit = self.OPPOSITE_BITS[(dx, dy)]
                if neighbor_cell & opp_bit:
                    continue

                visited[ny][nx] = True
                parent[ny][nx] = (cx, cy)
                queue.append((nx, ny))

        # No path found
        return None
