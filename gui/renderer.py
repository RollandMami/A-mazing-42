from gui.config import CELL_SIZE, MARGIN
import gui.colors as colors
from typing import Any, Optional


class Renderer:
    """Renders maze structures and UI overlays onto a MiniLibX image buffer.

    Manages off-screen image buffer allocations, frame clearing,
    pixel color writes,
    dynamic cell scaling, and window updates.
    """
    def __init__(self,
                 mlx_instance: Any,
                 mlx_ptr: Any, win_ptr: Any,
                 win_width: int = 1000,
                 win_height: int = 700) -> None:
        """Initializes the Renderer with window dimensions and
        MiniLibX handles.

        Args:
            mlx_instance: The PatchedMlx wrapper instance.
            mlx_ptr: Pointer to the initialized MiniLibX instance.
            win_ptr: Pointer to the active MiniLibX window instance.
            win_width: Width of the window in pixels. Defaults to 1000.
            win_height: Height of the window in pixels. Defaults to 700.
        """
        self.mlx = mlx_instance
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self._win_width = win_width
        self._win_height = win_height
        self._img_ptr = None
        self._img_data: Optional[bytearray] = None
        self._img_sizeline: int = 0

    def _pixel(self, x: int, y: int, color: Any) -> None:
        """Sets a single pixel color within the off-screen image buffer.

        Args:
            x: Horizontal pixel coordinate.
            y: Vertical pixel coordinate.
            color: Bitwise integer color representation (0xRRGGBB).
        """
        if x < 0 or x >= self._win_width or y < 0 or y >= self._win_height \
           or not self._img_data:
            return
        offset: int = y * self._img_sizeline + x * 4
        self._img_data[offset] = (color >> 0) & 0xFF
        self._img_data[offset + 1] = (color >> 8) & 0xFF
        self._img_data[offset + 2] = (color >> 16) & 0xFF
        self._img_data[offset + 3] = 255

    def _fill_rect(self, x0: int, y0: int, x1: int, y1: int, color: Any
                   ) -> None:
        """Fills a rectangular region in the image buffer with a solid color.

        Args:
            x0: Upper-left horizontal coordinate.
            y0: Upper-left vertical coordinate.
            x1: Lower-right horizontal coordinate.
            y1: Lower-right vertical coordinate.
            color: Bitwise integer color representation (0xRRGGBB).
        """
        if not self._img_data:
            return
        for y in range(max(0, y0), min(self._win_height, y1 + 1)):
            row_start = y * self._img_sizeline
            for x in range(max(0, x0), min(self._win_width, x1 + 1)):
                offset = row_start + x * 4
                self._img_data[offset] = (color >> 0) & 0xFF
                self._img_data[offset + 1] = (color >> 8) & 0xFF
                self._img_data[offset + 2] = (color >> 16) & 0xFF
                self._img_data[offset + 3] = 255

    def _fill_entire_background(self, color: Any) -> None:
        """Fills the entire image buffer with a background color.

        Args:
            color: Bitwise integer color representation (0xRRGGBB).
        """
        if not self._img_data:
            return
        for y in range(self._win_height):
            row_start = y * self._img_sizeline
            for x in range(self._win_width):
                offset = row_start + x * 4
                self._img_data[offset] = (color >> 0) & 0xFF
                self._img_data[offset + 1] = (color >> 8) & 0xFF
                self._img_data[offset + 2] = (color >> 16) & 0xFF
                self._img_data[offset + 3] = 255

    def _draw_wall_line(self, x0: int, y: int, x1: int, color: Any) -> None:
        """Draws a horizontal line in the image buffer.

        Args:
            x0: Starting horizontal pixel coordinate.
            y: Vertical pixel coordinate of the line.
            x1: Ending horizontal pixel coordinate.
            color: Bitwise integer color representation (0xRRGGBB).
        """
        if y < 0 or y >= self._win_height or not self._img_data:
            return
        row_start = y * self._img_sizeline
        for x in range(max(0, x0), min(self._win_width, x1 + 1)):
            offset = row_start + x * 4
            self._img_data[offset] = (color >> 0) & 0xFF
            self._img_data[offset + 1] = (color >> 8) & 0xFF
            self._img_data[offset + 2] = (color >> 16) & 0xFF
            self._img_data[offset + 3] = 255

    def _draw_wall_col(self, x: int, y0: int, y1: int, color: int) -> None:
        """Draws a vertical line in the image buffer.

        Args:
            x: Horizontal pixel coordinate of the column.
            y0: Starting vertical pixel coordinate.
            y1: Ending vertical pixel coordinate.
            color: Bitwise integer color representation (0xRRGGBB).
        """
        if x < 0 or x >= self._win_width or not self._img_data:
            return
        for y in range(max(0, y0), min(self._win_height, y1 + 1)):
            offset = y * self._img_sizeline + x * 4
            self._img_data[offset] = (color >> 0) & 0xFF
            self._img_data[offset + 1] = (color >> 8) & 0xFF
            self._img_data[offset + 2] = (color >> 16) & 0xFF
            self._img_data[offset + 3] = 255

    def _compute_cell_size(self, rows: int, cols: int) -> int:
        """Calculates the maximum fitting cell size in pixels for
        a given grid dimensions.

        Args:
            rows: Number of grid rows.
            cols: Number of grid columns.

        Returns:
            int: Calculated pixel size for each grid cell, bounded
            by minimum and maximum constraints.
        """
        TEXT_AREA = 100
        available_w = self._win_width - 2 * MARGIN
        available_h = self._win_height - 2 * MARGIN - TEXT_AREA
        fit_w = available_w // cols if cols > 0 else CELL_SIZE
        fit_h = available_h // rows if rows > 0 else CELL_SIZE
        return max(4, min(CELL_SIZE, fit_w, fit_h))

    def _ensure_image_buffer(self) -> None:
        """Ensures an off-screen image buffer is created and bound
        to MLX data pointers.

        Raises:
            RuntimeError: If MiniLibX fails to allocate the image pointer.
        """
        if self._img_ptr is not None:
            return
        self._img_ptr = self.mlx.mlx_new_image(
            self.mlx_ptr, self._win_width, self._win_height
        )
        if self._img_ptr is None:
            raise RuntimeError("error creating buffer image MLX")
        data, bpp, sizeline, fmt = self.mlx.mlx_get_data_addr(self._img_ptr)
        self._img_data = data
        self._img_sizeline = sizeline

    def _put_image(self) -> None:
        """Pushes the off-screen image buffer to the active window."""
        if self._img_ptr is not None:
            self.mlx.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self._img_ptr, 0, 0
            )

    def clear(self) -> None:
        """Clears the off-screen buffer with the default background
        color and displays it."""
        self._ensure_image_buffer()
        self._fill_entire_background(colors.BACKGROUND_COLOR)
        self._put_image()

    def draw_maze(self, grid: Any, entry: Any = None, exit_pos: Any = None,
                  path: Any = None, show_path: Any = False,
                  forty_two_positions: Any = None, generation_time: Any = None
                  ) -> None:
        """Renders the complete maze grid, special markers, solution paths,
        and HUD text.

        Args:
            grid: 2D array of bitwise wall values representing the maze cells.
            entry: Optional tuple `(col, row)` of the entrance cell.
            exit_pos: Optional tuple `(col, row)` of the exit cell.
            path: Optional list of coordinate tuples along the
            solved solution path.
            show_path: Boolean flag indicating whether to render
            the solution path overlay.
            forty_two_positions: Optional set of coordinate tuples
            forming the '42' mask cells.
            generation_time: Optional generation duration
            readout (reserved for future display).
        """
        self._ensure_image_buffer()

        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)

        if not grid or len(grid) == 0:
            self._fill_entire_background(colors.BACKGROUND_COLOR)
            self._put_image()
            return

        if forty_two_positions is None:
            forty_two_positions = set()

        path_set = {tuple(p) for p in path} if path else set()

        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0

        cell_size = self._compute_cell_size(rows, cols)

        maze_w = cols * cell_size
        maze_h = rows * cell_size

        self._fill_entire_background(colors.BACKGROUND_COLOR)

        WALL_W = max(1, cell_size // 12)

        for row_idx in range(rows):
            for col_idx in range(cols):
                x0 = MARGIN + col_idx * cell_size
                y0 = MARGIN + row_idx * cell_size
                x1 = x0 + cell_size - 1
                y1 = y0 + cell_size - 1
                cell_value = grid[row_idx][col_idx]
                is_entry = entry is not None and (col_idx, row_idx) == entry
                in_path = show_path and (col_idx, row_idx) in path_set
                has_42 = (col_idx, row_idx) in forty_two_positions
                is_exit = exit_pos is not None and (
                    col_idx, row_idx) == exit_pos

                fill_color = None
                if in_path:
                    fill_color = colors.PATH_COLOR
                elif is_entry:
                    fill_color = colors.ENTRY_COLOR
                elif is_exit:
                    fill_color = colors.EXIT_COLOR
                elif has_42:
                    fill_color = colors.FORTY_TWO_COLOR

                if fill_color is not None:
                    self._fill_rect(
                        x0 + WALL_W,
                        y0 + WALL_W,
                        x1 - WALL_W,
                        y1 - WALL_W,
                        fill_color)

                if cell_value & 0x1:
                    for t in range(WALL_W):
                        self._draw_wall_line(
                            x0 - t, y0 - t, x1 + t, colors.WALL_COLOR)
                if cell_value & 0x2:
                    for t in range(WALL_W):
                        self._draw_wall_col(
                            x1 + t, y0 - t, y1 + t, colors.WALL_COLOR)
                if cell_value & 0x4:
                    for t in range(WALL_W):
                        self._draw_wall_line(
                            x0 - t, y1 + t, x1 + t, colors.WALL_COLOR)
                if cell_value & 0x8:
                    for t in range(WALL_W):
                        self._draw_wall_col(
                            x0 - t, y0 - t, y1 + t, colors.WALL_COLOR)

        for t in range(WALL_W):
            self._draw_wall_line(
                MARGIN - t, MARGIN - t, MARGIN + maze_w + t, colors.WALL_COLOR)
            self._draw_wall_line(
                MARGIN - t, MARGIN + maze_h + t,
                MARGIN + maze_w + t, colors.WALL_COLOR)
            self._draw_wall_col(
                MARGIN - t, MARGIN - t, MARGIN + maze_h + t, colors.WALL_COLOR)
            self._draw_wall_col(
                MARGIN + maze_w + t, MARGIN - t,
                MARGIN + maze_h + t, colors.WALL_COLOR)

        self._put_image()

        bottom_y = self._win_height - 90

        self.mlx.mlx_string_put(
            self.mlx_ptr, self.win_ptr,
            MARGIN, bottom_y,
            colors.TEXT_COLOR,
            "'r' regenerate, 'c' colors theme, "
            "'p' -> path, 'Esc' -> quit"
        )
