import os
from typing import List, Tuple, Set, Any

from gui.config import MAZE_NBR
from mazegen import Config  # type: ignore[import-untyped]
from mazegen import TxtWriter
from mazegen import PrimGenerator
from mazegen import BaseGen


def parse_maze_file(path: str) -> Tuple[
                        List[List[int]],
                        Tuple[int, int],
                        Tuple[int, int]]:
    with open(path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) < 3:
        raise ValueError("invalid maze file : too small lines")

    entry_line = lines[-2]
    exit_line = lines[-1]

    entry_parts = entry_line.strip("()").split(",")
    exit_parts = exit_line.strip("()").split(",")
    entry: Tuple[int, int] = (int(entry_parts[0]), int(entry_parts[1]))
    exit_pos: Tuple[int, int] = (int(exit_parts[0]), int(exit_parts[1]))

    grid_lines = lines[:-2]
    grid: List[List[int]] = []
    for line in grid_lines:
        line = line.strip()
        row = [int(ch, 16) for ch in line]
        grid.append(row)

    return grid, entry, exit_pos


def get_42_positions(mask_42_list: List[Tuple[int, int]]
                     ) -> Set[Tuple[int, int]]:
    return set(mask_42_list) if mask_42_list else set()


def load_maze_from_file(path: str = "maze.txt") -> dict[str, Any]:
    grid, entry, exit_pos = parse_maze_file(path)
    return {
        "grid": grid,
        "entry": entry,
        "exit_pos": exit_pos,
        "forty_two_positions": set(),
    }


def _create_default_config(path: str) -> None:
    n = MAZE_NBR
    content = f"""
WIDTH={n}
HEIGHT={n}
ENTRY=0,{n//2}
EXIT={n-1},{n//2}
OUTPUT_FILE=maze.txt
PERFECT=False
ALGORITHM=1
"""
    with open(path, "w") as f:
        f.write(content)
    print(f"Configuration file created : {path}")
    print(f"Dimensions : {n}x{n}")


def generate_new_maze(config_path: str = "config.txt") -> dict[str, Any]:
    _create_default_config(config_path)

    cfg = Config(config_path)
    writer = TxtWriter()
    engine: BaseGen = PrimGenerator(cfg, writer)

    print("Generating new maze...")
    engine.generate()
    engine.export()
    print(f"Maze exporting into {cfg.output_file}")

    output_path = cfg.output_file
    if not os.path.isabs(output_path):
        output_path = os.path.join(os.getcwd(), output_path)

    grid, entry, exit_pos = parse_maze_file(output_path)
    forty_two: set[tuple[int, int]] = set()
    if hasattr(engine, '_mask_42') and engine._mask_42:
        forty_two = get_42_positions(engine._mask_42)
    else:
        forty_two = set()

    return {
        "grid": grid,
        "entry": entry,
        "exit_pos": exit_pos,
        "forty_two_positions": forty_two,
    }
