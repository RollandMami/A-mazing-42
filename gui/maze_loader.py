import os
from typing import List, Any, Optional
import sys

from mazegen import MazeGenerator
try:
    from pydantic import BaseModel, field_validator, model_validator
except Exception as e:
    print(f"{type(e).__name__}: {e}")


class MazeModel(BaseModel):
    """Pydantic model representing structured and validated maze data.

    Attributes:
        grid (list[list[int]]): 2D grid containing bitwise integer wall values.
        entry (tuple[int, int]): Starting coordinates `(column, row)`.
        exit_pos (tuple[int, int]): Ending target coordinates `(column, row)`.
        forty_two_positions (set[tuple[int, int]]): Set of coordinate
        tuples forming the '42' logo mask.
        path (Optional[list[tuple[int, int]]]): Solved path represented
        as a list of coordinate tuples.
    """
    grid: list[list[int]]
    entry: tuple[int, int]
    exit_pos: tuple[int, int]
    forty_two_positions: set[tuple[int, int]]
    path: Optional[list[tuple[int, int]]] = None

    @field_validator("entry", "exit_pos", mode="before")
    @classmethod
    def parse_coordinate_tuple(cls, value: object) -> object:
        """Parses raw inputs into valid 2D coordinate tuples.

        Accepts existing integer tuples or parses string representations
        such as `"(x, y)"` or `"x, y"`.

        Args:
            value: Raw input coordinate data (tuple or string).

        Returns:
            A tuple of two integers `(x, y)`.

        Raises:
            ValueError: If the input cannot be parsed into
            a 2-integer coordinate tuple.
        """
        # Si la valeur est déjà un tuple de 2 entiers, on la laisse passer
        if isinstance(value, tuple):
            return value

        # Si la valeur arrive sous forme de chaîne de caractères
        if isinstance(value, str):
            # Nettoyage des parenthèses, espaces et découpage
            cleaned = value.strip("() ").split(",")
            if len(cleaned) == 2:
                try:
                    return (int(cleaned[0].strip()), int(cleaned[1].strip()))
                except ValueError:
                    raise ValueError(f"Invalid Coords : '{value}'")

        raise ValueError(f"Invalid coords format : {value}")

    @model_validator(mode="after")
    def validate_bounds(self) -> "MazeModel":
        """Ensures entry and exit coordinates fall within the grid dimensions.

        Returns:
            MazeModel: The validated model instance.

        Raises:
            ValueError: If entry or exit points are out of grid bounds.
        """
        height = len(self.grid)
        width = len(self.grid[0]) if height else 0
        for name, pt in [("entry", self.entry), ("exit_pos", self.exit_pos)]:
            x, y = pt
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(
                    f"{name} {pt} is out of bounds ({width}x{height})")
        return self


class MazeData:
    """Manager class for loading, storing, and generating maze data structures.

    Attempts to read maze files from disk and validates them with `MazeModel`.
    If the file is missing or corrupted, it triggers maze
    generation automatically.
    """

    def __init__(self, cfg_path: str = "config.txt",
                 maze_path: Optional[str] = None) -> None:
        """Initializes MazeData with configuration and target maze file paths.

        Args:
            cfg_path: Path to the maze generator configuration file.
            maze_path: Optional path to an existing maze file.
            Defaults to config output path.
        """
        self.cfg_path = cfg_path
        self.generators: MazeGenerator = MazeGenerator.from_config(cfg_path)
        output_path = maze_path or self.generators.output_file
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
        self.src = output_path

        self.forty_two: set[tuple[int, int]] = set(
            self.generators.mask_42 or []
        )
        try:
            raw = self.load_maze_from_file()
        except FileNotFoundError:
            sys.exit(1)
        except ValueError as e:
            print(f"Corrupted maze file detected, regenerating: {e}")
            sys.exit(1)
        self.data: MazeModel = MazeModel.model_validate(raw)

    @property
    def grid(self) -> list[list[int]]:
        """list[list[int]]: The 2D grid matrix of the maze."""
        return self.data.grid

    @property
    def entry(self) -> tuple[int, int]:
        """tuple[int, int]: Entrance coordinates `(column, row)`."""
        return self.data.entry

    @property
    def exit_pos(self) -> tuple[int, int]:
        """tuple[int, int]: Exit coordinates `(column, row)`."""
        return self.data.exit_pos

    @property
    def path(self) -> Optional[list[tuple[int, int]]]:
        """Optional[list[tuple[int, int]]]: Solved path coordinate
        steps, if available."""
        return self.data.path

    def load_maze_from_file(self) -> dict[str, Any]:
        """Reads and parses raw maze data from a formatted text file.

        Returns:
            dict[str, Any]: Dictionary containing parsed `grid`, `entry`,
            `exit_pos`, `forty_two_positions`, and `path`.

        Raises:
            ValueError: If the file content is improperly
            formatted or corrupted.
            FileNotFoundError: If the file does not exist at `self.src`.
        """
        try:
            with open(self.src, "r") as f:
                lines = [line.strip() for line in f if line.strip()]

            if len(lines) < 4:
                raise ValueError("invalid maze file : too small lines")

            entry_line = lines[-3]
            exit_line = lines[-2]
            path_str = lines[-1]

            grid_lines = lines[:-3]
            grid: List[List[int]] = []
            for line in grid_lines:
                line = line.strip()
                row = [int(ch, 16) for ch in line]
                grid.append(row)

            entry = self._parse_coord(entry_line)
            exit_pos = self._parse_coord(exit_line)
            return {
                    "grid": grid,
                    "entry": entry,
                    "exit_pos": exit_pos,
                    "forty_two_positions": self.forty_two,
                    "path": self.convert_path(path_str, entry, exit_pos)
                    }
        except (ValueError, IndexError) as e:
            raise ValueError(f"Corrupted maze file: {e}") from e
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
            raise

    def generate_new_maze(self) -> dict[str, Any]:
        """Generates a new maze using the generator instance
        and exports it to disk.

        Returns:
            dict[str, Any]: Raw data dictionary containing
            generated `grid`, `entry`,
            `exit_pos`, `forty_two_positions`, and `path`.

        Raises:
            ValueError: If the generated maze has no valid
            path between entry and exit.
        """
        print("Generating new maze...")
        self.generators.generate()
        self.generators.export()
        print(f"Maze exporting into {self.generators.output_file}")

        solution = self.generators.get_solution()
        if solution is None:
            raise ValueError(
             "Maze has no valid solution between entry and exit")
        return {
            "grid": self.generators.get_grid(),
            "entry": self.generators.entry,
            "exit_pos": self.generators.exit_pos,
            "forty_two_positions": self.forty_two,
            "path": solution
        }

    @staticmethod
    def convert_path(path: str,
                     start: tuple[int, int],
                     end: tuple[int, int]
                     ) -> list[tuple[int, int]]:
        """Converts a cardinal direction string (e.g. 'NESW')
        into coordinate steps.

        Args:
            path: String sequence of movement directions ('N', 'E', 'S', 'W').
            start: Starting coordinate tuple `(x, y)`.
            end: Target ending coordinate tuple `(x, y)`.

        Returns:
            list[tuple[int, int]]: Sequential list of coordinate
            tuples along the path.

        Raises:
            ValueError: If traversing the direction string does not
            terminate at `end`.
        """
        DIRECTIONS_Dict = {
            'N': (0, -1),
            'E': (1,  0),
            'S': (0,  1),
            'W': (-1, 0)
        }
        cx, cy = start
        result: list[tuple[int, int]] = [start]
        for c in path:
            cx += DIRECTIONS_Dict[c][0]
            cy += DIRECTIONS_Dict[c][1]
            result.append((cx, cy))
        fx, fy = end
        if cx != fx or cy != fy:
            raise ValueError(
                f"Path error, does not end at {end}, got ({cx},{cy})")
        return result

    @staticmethod
    def _parse_coord(value: str) -> tuple[int, int]:
        """Parses a string formatted as '(x, y)' into an
        integer coordinate tuple.

        Args:
            value: Raw string coordinate input.

        Returns:
            tuple[int, int]: Parsed `(x, y)` integer pair.

        Raises:
            ValueError: If string format cannot be split
            into exactly two integers.
        """
        cleaned = value.strip("() ").split(",")
        if len(cleaned) != 2:
            raise ValueError(f"Invalid coords format: {value}")
        return (int(cleaned[0].strip()), int(cleaned[1].strip()))


if __name__ == "__main__":
    MazeData().load_maze_from_file()
