#!/usr/bin/env python3
from typing import Optional, Any


class EventHandler:

    def __init__(self,
                 mlx_instance: Any,
                 mlx_ptr: Any,
                 win_ptr: Any,
                 window: Any) -> None:
        self.mlx = mlx_instance
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self.window = window

    def setup_hooks(self) -> None:
        self.mlx.mlx_key_hook(self.win_ptr, self._on_key, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self._on_destroy, None)

    def _on_destroy(self, param: Optional[Any]) -> None:
        print("Windows closed succesfuly!")
        self.mlx.mlx_loop_exit(self.mlx_ptr)

    def _on_key(self, keycode: int, param: Optional[Any]) -> None:
        if keycode == 65307:
            self.mlx.mlx_loop_exit(self.mlx_ptr)
        elif keycode == 114 or keycode == 82:
            self._regenerate_maze()

        elif keycode == 112 or keycode == 80:
            self._toggle_path()

        elif keycode == 99 or keycode == 67:
            self._cycle_wall_color()

    def _regenerate_maze(self) -> None:
        print("New maze creating...")
        self.window.regenerate_maze()

    def _toggle_path(self) -> None:
        self.window.toggle_path()

    def _cycle_wall_color(self) -> None:
        import gui.colors as colors_module
        current = colors_module.WALL_COLOR
        palette = [0xFFFFFF, 0xFF0000, 0x00FF00, 0x0000FF]
        idx = 0
        for i, c in enumerate(palette):
            if current == c:
                idx = (i + 1) % len(palette)
                break
        colors_module.WALL_COLOR = palette[idx]
        print(f"Wall color changed : #{palette[idx]:06X}")
        self.window.render()
