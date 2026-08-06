# Mazegen - Maze Generator Module

`mazegen` is a Python library designed to procedurally generate mazes with strict structural constraints, seed reproducibility, and pathfinding solution export.

---

## 📋 Features & Compliance (IV.4 Maze Requirements)

This library strictly adheres to the following specification requirements:

* **Seed Reproducibility:** Every maze generation algorithm accepts an optional integer `seed`. Using the same seed guarantees identical maze outputs across runs.
* **4-Cardinal Walls:** Each cell tracks walls on all four cardinal directions: **North**, **East**, **South**, and **West**.
* **Boundary & Validity Constraints:**
  * **Entry & Exit:** Validated via Pydantic (`ConfigModel`). Must be distinct and strictly located within maze bounds ($0 \le x < 	WIDTH) ($0 \le y < 	HEIGHT). Outer borders feature enclosing walls.
  * **Connectivity:** Ensures full grid connectivity with zero isolated/unreachable cells (excluding the protected `'42'` pattern).
  * **Wall Coherence:** Neighboring cells share consistent wall states. If Cell $(x, y)$ has an **East** wall, Cell $(x+1, y)$ strictly has a **West** wall.
* **Open Area Prevention:** Prevents large open plazas. Open areas larger than $2times3$ or $3times2$ (e.g., $3	imes3$) are prohibited.
* **Embedded "42" Pattern:** Generates a visually recognizable **"42"** pattern using fully closed/filled cells.
* **Perfect Maze Mode (`PERFECT=True`):** When activated, guarantees **exactly one unique path** between the Entry and Exit cells (spanning tree structure).

---

## 🛠️ Building & Packaging (`mazegen-*`)

The project supports standard packaging tools (`setuptools` / `flit` / `poetry` / `hatchling`).

### 1. Build the Package Distribution
From the root of your Git repository:

```bash
# Using standard build tool
python3 -m pip install --upgrade build
python3 -m build
```

This generates build artifacts in the `dist/` directory:
* `dist/mazegen-1.0.0-py3-none-any.whl`
* `dist/mazegen-1.0.0.tar.gz`

---

## 📦 Installation Guide

### Option A: Install in a Virtual Environment (`venv`)

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install from the built wheel (.whl) or source tarball (.tar.gz)
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

### Option B: Install with Poetry

```bash
# Add local wheel package to Poetry project
poetry add ./dist/mazegen-1.0.0-py3-none-any.whl
```

---

## 🚀 Quickstart & Usage Example

Below is a basic example demonstrating how to import `MazeGenerator`, configure custom parameters, generate a maze, and extract the grid structure & path solution.

```python
from mazegen import MazeGenerator

# 1. Instantiate the generator with custom parameters
generator = MazeGenerator(
    width=20,
    height=20,
    entry=(0, 0),
    exit_pos=(19, 19),
    seed=42,
    perfect=True,
    algorithm="dfs"
)

# 2. Generate the maze grid structure
generator.generate()

# 3. Access internal maze structure
grid_data = generator.get_grid()
print(f"Maze dimensions: {generator.width}x{generator.height}")

# 4. Access the path solution
solution_path = generator.get_solution()
print(f"Path from Entry to Exit ({len(solution_path)} steps):")
print(solution_path)
```

---

## ⚙️ Module API Reference

### `MazeGenerator` Class

```python
class MazeGenerator:
    def __init__(
        self,
        width: int = 15,
        height: int = 15,
        entry: tuple[int, int] = (0, 0),
        exit_pos: tuple[int, int] = (14, 14),
        seed: int | None = None,
        perfect: bool = True,
        algorithm: str = "dfs" # {0:"dfs", 1:"prim"}
    ) -> None: ...

    def generate(self) -> None:
        """Generates the maze grid according to configuration."""

    def get_grid(self) -> list[list[int]]:
        """Returns the matrix representation of the maze."""

    def get_solution(self) -> list[tuple[int, int]]:
        """Returns ordered list of (x, y) coordinates from Entry to Exit."""
```
