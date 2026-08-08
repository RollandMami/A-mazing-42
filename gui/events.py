#!/usr/bin/env python3
"""Module for handling user input events and window signals.

This module intercepts keyboard inputs and MiniLibX window destruction events,
dispatching appropriate actions to control the maze application interface.
"""

from typing import Any
from . import colors as colors_module


class EventHandler:
    """Manages input hooks, key bindings, and window callbacks for MiniLibX.

    This handler translates keypresses into maze control actions (regenerating,
    toggling paths, cycling color themes, or exiting the application).
    """

    def __init__(self,
                 mlx_instance: Any,
                 mlx_ptr: Any,
                 win_ptr: Any,
                 window: Any) -> None:
        """Initializes the event handler with MiniLibX
        instances and window reference.

        Args:
            mlx_instance: The PatchedMlx wrapper instance.
            mlx_ptr: Pointer to the initialized MiniLibX instance.
            win_ptr: Pointer to the active MiniLibX window instance.
            window: Reference to the parent Window controller object.
        """
        self.mlx = mlx_instance
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self.window = window
        self._bindings = {
            65307: lambda: self.mlx.mlx_loop_exit(self.mlx_ptr),
            ord('r'): self.window.regenerate_maze,
            ord('R'): self.window.regenerate_maze,
            ord('p'): self.window.toggle_path,
            ord('P'): self.window.toggle_path,
            ord('c'): self._cycle_wall_color,
            ord('C'): self._cycle_wall_color,
        }

    def setup_hooks(self) -> None:
        """Register keyboard and window-close event hooks."""
        self.mlx.mlx_key_hook(self.win_ptr, self._on_key, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self._on_destroy, None)

    def _on_destroy(self, param: Any) -> None:
        """Handles the window-close (WM_DELETE_WINDOW) event.

        Args:
            param: Optional parameter passed by the MiniLibX event hook.
        """
        print("Windows closed succesfuly!")
        self.mlx.mlx_loop_exit(self.mlx_ptr)

    def _on_key(self, keycode: int, param: Any) -> None:
        """Dispatches a keypress event to its bound callback function.

        Args:
            keycode: Key code integer sent by the MiniLibX keypress hook.
            param: Optional parameter passed by the MiniLibX event hook.
        """
        action = self._bindings.get(keycode)
        if action:
            try:
                action()
            except Exception as e:
                print("Erreur pendant l'action clavier",
                      f" : {type(e).__name__}: {e}", sep="")

    def _cycle_wall_color(self) -> None:
        """Cycles through predefined wall color palettes and
        re-renders the maze."""
        current = colors_module.WALL_COLOR
        palette = [
            0xFFFFFF,
            0xFF0000,
            0x00FF00,
            0x0000FF]
        idx = 0
        for i, c in enumerate(palette):
            if current == c:
                idx = (i + 1) % len(palette)
                break
        colors_module.WALL_COLOR = palette[idx]
        print(f"Wall color changed : #{palette[idx]:06X}")
        self.window.render()
