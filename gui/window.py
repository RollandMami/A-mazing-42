#!/usr/bin/env/ python3
import sys
from typing import Any, Optional
import time
import signal
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
from .renderer import Renderer
from .events import EventHandler
from .maze_loader import MazeData
from mazegen import MazeGenerator


class Window:
    """Main window controller managing UI lifecycle,
    animations, and event loops.

    Serves as the central state holder for maze data,
    path solving visualization,
    and progressive frame-rate-regulated loading animations.
    """
    def __init__(self) -> None:
        """Initializes the MiniLibX window instance,
        renderer, and event handlers.

        Sets up graphic context, memory structures for
        animations, and defaults time-tracking flags.
        """
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

        self.grid: Optional[Any] = None
        self.entry: Optional[tuple[int, int]] = None
        self.exit_pos: Optional[tuple[int, int]] = None
        self.path: Optional[Any] = None
        self.show_path = False
        self.forty_two_positions: set[Any] = set()
        self.generation_time = None
        self._solver = MazeGenerator()._engine._solver

        # animation variable
        self.display_grid: list[Any] = []
        self.animation = False
        self.animation_index = 0
        self.full_path: list[Any] = []

        self.generation_animation = False
        self.generation_steps: list[Any] = []
        self.generation_index = 0
        self.generation_row = 0
        self.generation_col = 0

        self.last_frame = time.time()

    def _handle_terminal_interrupt(self, signum: int, frame: Any) -> None:
        """Intercepts Ctrl+C (SIGINT) and Ctrl+Z (SIGTSTP) to avoid raising
        KeyboardInterrupt in the middle of a ctypes/MiniLibX callback.

        MiniLibX callbacks are invoked from C through ctypes, which cannot
        propagate a Python exception back through the C call stack. Letting
        the default SIGINT/SIGTSTP behaviour fire mid-callback produces the
        ugly "Exception ignored on calling ctypes callback function"
        traceback instead of a clean shutdown message. Handling the signal
        ourselves means we run as normal Python code (no exception raised),
        so nothing needs to cross the ctypes boundary.

        Args:
            signum: Signal number received (SIGINT or SIGTSTP).
            frame: Current stack frame (unused, required by signal API).
        """
        print(
            "\nVeuillez utiliser le bouton [X] de la fenêtre "
            "ou la touche Echap du clavier pour quitter proprement."
            "You are crazy guys XP"
        )

    def _install_signal_handlers(self) -> None:
        """Registers custom handlers for SIGINT (Ctrl+C) and SIGTSTP
        (Ctrl+Z) so they display a clean message instead of interrupting
        a MiniLibX ctypes callback mid-flight."""
        signal.signal(signal.SIGINT, self._handle_terminal_interrupt)
        if hasattr(signal, "SIGTSTP"):
            signal.signal(signal.SIGTSTP, self._handle_terminal_interrupt)

    def load_maze(self,
                  grid: Any,
                  entry: Optional[tuple[int, int]] = None,
                  exit_pos: Optional[tuple[int, int]] = None,
                  path: Any = None,
                  forty_two_positions: Any = None,
                  generation_time: Any = None
                  ) -> None:
        """Populates window state with new maze data and prepares
        grid animation flags.

        Args:
            grid: 2D array representing maze bitwise wall integers.
            entry: Optional entrance coordinate tuple `(col, row)`.
            exit_pos: Optional exit coordinate tuple `(col, row)`.
            path: Optional list of solution coordinate tuples.
            forty_two_positions: Optional set of coordinate tuples
            forming the '42' mask.
            generation_time: Elapsed generation time float in seconds.
        """
        self.grid = grid
        self.entry = entry
        self.exit_pos = exit_pos
        self.path = path
        self.forty_two_positions = forty_two_positions or set()
        self.show_path = False
        self.generation_time = generation_time
        rows = len(self.grid)
        cols = len(self.grid[0])

        self.display_grid = [
            [0 for _ in range(cols)]
            for _ in range(rows)
        ]
        self.generation_row = 0
        self.generation_col = 0
        self.generation_animation = True

    def render(self) -> None:
        """Invokes the Renderer to draw the active state
        onto the MiniLibX window."""
        self.renderer.draw_maze(
            self.display_grid,
            entry=self.entry,
            exit_pos=self.exit_pos,
            path=self.path,
            show_path=self.show_path,
            forty_two_positions=self.forty_two_positions,
            generation_time=self.generation_time,
        )

    def load_initial_maze(self, maze_file: str) -> None:
        """Loads and initializes maze data from a file path.

        Args:
            maze_file: File system path pointing to a formatted maze text file.
        """
        try:
            data = MazeData(maze_path=maze_file)
            self.load_maze(
                data.grid,
                entry=data.entry,
                exit_pos=data.exit_pos,
                path=data.path,
                forty_two_positions=data.forty_two,
                generation_time=None,
            )
        except (FileNotFoundError, ValueError) as e:
            print(f"Error : {e}")

    def regenerate_maze(self, cfg: str | None = None) -> bool:
        """Triggers generator logic to create and load a new maze structure.

        Args:
            cfg_path: Configuration file path string,
            or None to use default `"config.txt"`.
        """
        if not cfg:
            cfg = "config.txt"
        try:
            t_start = time.time()
            data = MazeData(cfg_path=cfg).generate_new_maze()
            elapsed = time.time() - t_start
            print(f"Maze generating in {elapsed:.3f}s")
            self.load_maze(
                data["grid"],
                entry=data["entry"],
                exit_pos=data["exit_pos"],
                path=data["path"],
                forty_two_positions=data["forty_two_positions"],
                generation_time=elapsed,
            )
            return True
        except Exception as e:
            print(f"Error : {e}")
            return False

    def toggle_path(self) -> None:
        """Toggles path visibility and triggers
        step-by-step path tracing animation."""
        if self.grid is None or self.entry is None or self.exit_pos is None:
            print("Missing maze loading to path!")
            return

        self.show_path = not self.show_path

        if self.show_path:
            solution = self._solver.solve(
                self.grid, self.entry, self.exit_pos)
            if solution is not None:
                path, _ = solution
                self.full_path = path
                self.path = []
                self.animation_index = 0
                self.animation = True
                print(f"Path found: {len(path)} walls")
            else:
                print("Path not found!")
                self.show_path = False
                self.path = None
        else:
            self.path = None
            self.animation = False
            self.full_path = []
            self.animation_index = 0
            self.render()
            print("Hide Path")

    def update(self, _: Any = None) -> None:
        """Frame update callback regulating frame
        rates and driving progressive animations.

        Executes at roughly 60 FPS, advancing progressive
        grid revelation cell-by-cell, followed by step-by-step
        path tracing once grid reveal completes.

        Args:
            _: Unused parameter required by MiniLibX loop hook signature.
        """
        now = time.time()

        # Contrôle du FPS / de la vitesse d'animation (~60 FPS)
        if now - self.last_frame < 0.016:
            return

        self.last_frame = now
        need_render = False

        # 1. Animation de génération de la grille
        if self.generation_animation and self.grid is not None:
            if self.generation_row < len(self.grid):
                self.display_grid[self.generation_row][self.generation_col] = \
                    self.grid[self.generation_row][self.generation_col]

                self.generation_col += 1
                if self.generation_col >= len(self.grid[0]):
                    self.generation_col = 0
                    self.generation_row += 1

                if self.generation_row >= len(self.grid):
                    self.generation_animation = False

                need_render = True

        # 2. Animation du chemin (Path)
        # On n'exécute l'animation de chemin QUE si la grille
        # a fini de se charger
        if self.animation and not self.generation_animation:
            if self.animation_index < len(self.full_path):
                if self.path is None:
                    self.path = []

                # Ajouter le pas actuel du chemin
                self.path.append(self.full_path[self.animation_index])
                self.animation_index += 1
                need_render = True
            else:
                self.animation = False

        if need_render:
            self.render()

    def run(self) -> None:
        """Configures hooks, draws initial elements, and launches the
        MiniLibX event loop."""
        self._install_signal_handlers()
        self.events.setup_hooks()

        self.mlx.mlx_loop_hook(
            self.mlx_ptr,
            self.update,
            None
        )

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
