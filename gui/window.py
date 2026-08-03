#!/usr/bin/env/ python3
import sys
from typing import Any, Optional
try:
    from gui.mlx_fix import PatchedMlx
except Exception as e:
    print(f"{type(e).__name__}: {e}")
    print("Make sure to install properly mlx\n")
    sys.exit(1)

from gui.config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
)
from gui.renderer import Renderer
from gui.events import EventHandler
from gui.maze_loader import load_maze_from_file, generate_new_maze

from mazegen import BfsSolver


import time


class Window:
    def __init__(self) -> None:
        self.mlx = PatchedMlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
        )

        self.renderer = Renderer(
            self.mlx, self.mlx_ptr, self.win_ptr,
            win_width=WINDOW_WIDTH,
            win_height=WINDOW_HEIGHT,
        )
        self.events = EventHandler(self.mlx, self.mlx_ptr, self.win_ptr, self)

        self.grid = None
        self.entry: Optional[tuple[int, int]] = None
        self.exit_pos: Optional[tuple[int, int]] = None
        self.path = None
        self.show_path = False
        self.forty_two_positions: set[Any] = set()
        self.generation_time = None
        self._solver = BfsSolver()

    def load_maze(self,
                  grid: Any,
                  entry: Optional[tuple[int, int]] = None,
                  exit_pos: Optional[tuple[int, int]] = None,
                  path: Any = None,
                  forty_two_positions: Any = None,
                  generation_time: Any = None
                  ) -> None:
        self.grid = grid
        self.entry = entry
        self.exit_pos = exit_pos
        self.path = path
        self.forty_two_positions = forty_two_positions or set()
        self.show_path = False
        self.generation_time = generation_time

    def render(self) -> None:
        self.renderer.draw_maze(
            self.grid,
            entry=self.entry,
            exit_pos=self.exit_pos,
            path=self.path,
            show_path=self.show_path,
            forty_two_positions=self.forty_two_positions,
            generation_time=self.generation_time,
        )

    def load_initial_maze(self, maze_file: str = "maze.txt") -> None:
        try:
            data = load_maze_from_file(maze_file)
            self.load_maze(
                data["grid"],
                entry=data["entry"],
                exit_pos=data["exit_pos"],
                path=None,
                forty_two_positions=data["forty_two_positions"],
                generation_time=None,
            )
        except (FileNotFoundError, ValueError) as e:
            print(f"Error : {e}")

    def regenerate_maze(self) -> None:
        try:
            t_start = time.time()
            data = generate_new_maze("config.txt")
            elapsed = time.time() - t_start
            print(f"Maze generating in {elapsed:.3f}s")
            self.load_maze(
                data["grid"],
                entry=data["entry"],
                exit_pos=data["exit_pos"],
                path=None,
                forty_two_positions=data["forty_two_positions"],
                generation_time=elapsed,
            )
            self.render()
        except Exception as e:
            print(f"Error : {e}")

    def toggle_path(self) -> None:
        if self.grid is None or self.entry is None or self.exit_pos is None:
            print("Missing maze loading to path!")
            return

        self.show_path = not self.show_path

        if self.show_path:
            path = self._solver.solve(self.grid, self.entry, self.exit_pos)
            if path:
                self.path = path
                print(f"Path found: {len(path)} walls")
            else:
                print("Path not found!")
                self.show_path = False
                self.path = None
        else:
            self.path = None
            print("Hide Path")

        self.render()

    def run(self) -> None:
        self.events.setup_hooks()

        if self.grid is not None:
            self.render()
        else:
            self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
            self.mlx.mlx_string_put(
                self.mlx_ptr, self.win_ptr,
                10, 10, 0xFFFFFF,
                "Press 'r' to generate maze!!!!!!!!!"
            )

        self.mlx.mlx_loop(self.mlx_ptr)
