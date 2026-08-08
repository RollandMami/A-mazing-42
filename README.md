*This project has been created as part of the 42 curriculum by mamiandr, arakotot.*

# A-Maze-ing 🌀

> *"This is the way"* — A Python maze generator, with hexadecimal-encoded export, automatic solving, and an interactive graphical display (MiniLibX).

---

## Table of Contents

- [A-Maze-ing 🌀](#a-maze-ing-)
	- [Table of Contents](#table-of-contents)
	- [Description](#description)
	- [Features](#features)
	- [Project structure](#project-structure)
	- [Instructions](#instructions)
		- [Requirements](#requirements)
		- [Installation](#installation)
		- [Generate a maze (CLI)](#generate-a-maze-cli)
		- [Graphical display (MLX)](#graphical-display-mlx)
		- [Makefile](#makefile)
		- [Building the reusable `mazegen` package](#building-the-reusable-mazegen-package)
	- [Configuration file](#configuration-file)
	- [Output file](#output-file)
	- [Generation algorithm](#generation-algorithm)
		- [Why this algorithm?](#why-this-algorithm)
	- [Reusable `mazegen` module](#reusable-mazegen-module)
		- [Installation](#installation-1)
		- [Basic usage](#basic-usage)
		- [Passing custom parameters (size, seed…)](#passing-custom-parameters-size-seed)
		- [Accessing the generated structure and the solution](#accessing-the-generated-structure-and-the-solution)
	- [Graphical interface controls](#graphical-interface-controls)
	- [Team and project management](#team-and-project-management)
		- [Roles](#roles)
		- [Planning](#planning)
		- [Retrospective](#retrospective)
		- [Tools used](#tools-used)
	- [Bonuses](#bonuses)
	- [Resources](#resources)
		- [Documentation and references](#documentation-and-references)
		- [Use of AI](#use-of-ai)

---

## Description

**A-Maze-ing** is a maze generator written in Python 3.10+. The program:

1. reads a configuration file (`WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `PERFECT`, etc.);
2. generates a maze (perfect or not) using a graph-traversal algorithm (Prim or DFS);
3. automatically computes the shortest path between the entry and the exit (BFS);
4. exports the result to a text file, as a grid of hexadecimal digits (one digit = a 4-wall bitmask per cell);
5. displays the generated maze in a graphical window (MiniLibX), with the ability to regenerate it, show/hide the solution path, and change the colors.

The core generation logic (configuration parsing, generation algorithms, solver, export) is isolated in a standalone, reusable Python package: **`mazegen`**.

## Features

- Generation of **perfect** mazes (a single path between entry and exit) or **imperfect** ones (with added loops/cycles).
- Two generation algorithms implemented: **randomized Prim** and **DFS (recursive backtracker)**.
- Automatic maze solving via **BFS** (shortest path), with the path reconstructed as `N`/`E`/`S`/`W` letters.
- **Seed**-based generation for reproducibility (deterministic randomness when `SEED` is provided).
- A visible **"42"** pattern drawn using a mask of protected cells (automatically skipped if the maze is too small, with a warning message).
- Robust error handling: invalid configuration, missing file, out-of-bounds coordinates, etc. (no crashes, clear error messages).
- **MiniLibX** graphical interface: on-the-fly regeneration, show/hide solution path, wall color cycling.
- The generation engine (`mazegen`) is packaged independently and installable via `pip`.

## Project structure

```
.
├── a_maze_ing.py            # Main entry point (CLI) — run with a config file
├── config.txt                # Default configuration file
├── Makefile
├── README.md
├── mazegen-*.whl / .tar.gz   # Pre-built reusable package, at the repository root
├── src/
│   ├── pyproject.toml        # `mazegen` package definition (Poetry build)
│   ├── poetry.lock
│   └── mazegen/
│       ├── __init__.py       # Exposes the package's public API (Config, TxtWriter, BaseGen, PrimGenerator, DfsGenerator, BfsSolver, MazeGenerator)
│       ├── core/
│       │   └── maze_engine.py   # `MazeGenerator`: high-level orchestrator (config → engine selection → generation → export)
│       ├── infrastructure/
│       │   ├── config_parser.py # `Config`/`ConfigModel` + Pydantic validation of the config file
│       │   ├── loaders.py       # `TxtLoader`: parsing of the `KEY=VALUE` config file (1000-line limit)
│       │   ├── writers.py       # `TxtWriter`: writing of the output file (hexadecimal grid)
│       │   └── Errors.py        # `ConfigError`
│       ├── generator/
│       │   ├── base_gen.py      # `BaseGen`: abstract class ("42" mask, imperfections, export)
│       │   ├── prim_gen.py      # `PrimGenerator`: generation using Prim's algorithm
│       │   ├── dfs_gen.py       # `DfsGenerator`: generation via depth-first search (DFS)
│       │   └── Errors.py        # `MazeError`, `GenerationError`
│       └── solver/
│           ├── base_solver.py   # `BaseSolver`: abstract solver interface
│           └── bfs_solver.py    # `BfsSolver`: shortest path (BFS) — currently the only implemented solver
└── gui/
    ├── window.py              # `Window`: main MLX loop, state of the displayed maze
    ├── renderer.py            # `Renderer`: pixel-by-pixel drawing of the maze into the MLX buffer
    ├── events.py              # `EventHandler`: keyboard event handling
    ├── maze_loader.py         # Bridge between `mazegen` and the display (generation + output parsing)
    ├── colors.py              # Color palette (walls, entry, exit, path, "42" pattern)
    ├── config.py              # Window constants (size, title, cell size…)
    └── mlx_fix.py             # ctypes bindings fix for the MLX library
```

## Instructions

### Requirements

- **Python 3.10+**
- [Poetry](https://python-poetry.org/) (used to package `mazegen`), or `pip`/`uv`/`pipx` if you prefer.
- The **MiniLibX (MLX)** library for Python, along with its system dependencies (X11), for the graphical display.
- [`pydantic`](https://docs.pydantic.dev/) (a `mazegen` dependency, installed automatically).

### Installation

```bash
# From the repository root
make install
```

Or manually:

```bash
cd src
poetry install          # installs mazegen + its dependencies (pydantic…)
# or, without Poetry:
pip install -e . --break-system-packages
```

### Generate a maze (CLI)

```bash
python3 a_maze_ing.py config.txt
```

- `a_maze_ing.py` is the project's main script.
- `config.txt` is the configuration file (see [Configuration file](#configuration-file)); a default file is provided at the repository root.
- The generated maze is written to the file defined by the `OUTPUT_FILE` key in the configuration.

### Graphical display (MLX)

```bash
make run
```

The graphical interface loads the generated maze (or generates a new one on demand) and displays it in a window. See [Graphical interface controls](#graphical-interface-controls).

### Makefile

| Target | Description |
|---|---|
| `make install` | Installs the project's dependencies (Poetry/pip). |
| `make run` | Runs the main program (generation + display). |
| `make debug` | Runs the main script with `pdb` (Python's built-in debugger). |
| `make lint` | Runs `flake8 .` and `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`. |
| `make lint-strict` | Runs `flake8 .` and `mypy . --strict`. |
| `make clean` | Removes temporary files (`__pycache__`, `.mypy_cache`, etc.). |

### Building the reusable `mazegen` package

The generation module is packaged independently (see [Reusable module](#reusable-mazegen-module)). To rebuild it from source:

```bash
cd src
pip install build --break-system-packages
python3 -m build
# → produces dist/mazegen-<version>-py3-none-any.whl and dist/mazegen-<version>.tar.gz
```

The resulting `.whl` (or `.tar.gz`) file must be copied to the repository root, as required by the subject.

## Configuration file

The configuration file must contain one `KEY=VALUE` pair per line. Lines starting with `#` are comments and are ignored.

| Key | Mandatory | Description | Example |
|---|---|---|---|
| `WIDTH` | ✅ | Maze width (number of cells), must be `> 0`. | `WIDTH=20` |
| `HEIGHT` | ✅ | Maze height, must be `> 0`. | `HEIGHT=15` |
| `ENTRY` | ✅ | Entry coordinates `x,y`, must be within the grid bounds. | `ENTRY=0,0` |
| `EXIT` | ✅ | Exit coordinates `x,y`, must be within the grid bounds. | `EXIT=19,14` |
| `OUTPUT_FILE` | ✅ | Output filename (must end with `.txt`, no whitespace). | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | ✅ | `True`/`False` — if `True`, the maze contains exactly one path between entry and exit. If `False`, loops are added (~10% of the internal walls are additionally broken). | `PERFECT=True` |
| `SEED` | optional | Random seed for reproducibility. If omitted, a random seed is generated (integer between 0 and 999). | `SEED=42` |
| `ALGORITHM` | optional | Generation algorithm: `0`/`DFS` = DFS *(default)*, `1`/`PRIM` = Prim. Accepts either the integer or the algorithm name (case-insensitive). A third, A\*-based algorithm is planned but not implemented yet. | `ALGORITHM=1` or `ALGORITHM=prim` |
| `DISPLAY_MODE` | optional | Reserved for a future alternative display mode. | `DISPLAY_MODE=default` |

Configuration file validation (types, bounds, coordinate format, output filename extension…) is handled with **Pydantic**. Any invalid configuration triggers a clear error message, without crashing the program.

A default `config.txt` file is provided at the repository root.

## Output file

The maze is written to the output file as a grid of **hexadecimal** digits, one line per row of cells. Each digit encodes which walls of the corresponding cell are closed, bit by bit:

| Bit (LSB → MSB) | Direction |
|---|---|
| 0 | North |
| 1 | East |
| 2 | South |
| 3 | West |

A bit set to `1` means the wall is closed, `0` means it is open. Example: `A` (`1010` in binary) means the **East** and **West** walls are closed.

After the grid, a blank line separates the following metadata:

```
<hexadecimal grid, one line per row>

<entry coordinates>
<exit coordinates>
<shortest path, as N/E/S/W letters>
```

## Generation algorithm

**Default algorithm: DFS / recursive backtracker** (`DfsGenerator`, `ALGORITHM=0` or unset).

Principle:
1. Start from the entry cell, pushed onto a stack and marked as visited.
2. While the stack is not empty: look at the cell on top of the stack, list its unvisited neighbors.
3. If it has at least one unvisited neighbor, pick one at random, break the wall between the two cells (on both sides, to guarantee consistency), mark it visited and push it onto the stack.
4. If it has none, pop it off the stack (backtrack).
5. If `PERFECT=False`, an additional pass randomly breaks ~10% of the internal walls (excluding the "42" pattern) to create loops.

A second algorithm, **randomized Prim's algorithm** (`PrimGenerator`), is also implemented and selectable with `ALGORITHM=1` (or `ALGORITHM=prim`) in the configuration file. It starts from a random cell, grows a "frontier" list of unvisited neighbors, and repeatedly connects a random frontier cell to an already-visited neighbor until the frontier is empty.

### Why this algorithm?

**DFS** was kept as the default because:

- it is simple to implement and reason about, and it guarantees a perfect maze (single spanning tree) by construction.
- it fits naturally with the entry point: generation starts directly from the configured `ENTRY` cell.
- it produces long, winding corridors with few branches, which reads well in the graphical display.

**Prim's algorithm** remains available as an alternative:

- it produces mazes with **many short branches** rather than long winding corridors — resulting in a more "organic" visual look, closer to a real-world maze.
- it fits naturally with the **protected-mask** logic (the "42" pattern): it is enough to exclude certain cells from the frontier list to guarantee they are never connected to the rest of the maze other than along their outline.
- its complexity remains reasonable (roughly `O(cells × 4)` thanks to the frontier structure), which allows large grids to be generated quickly without degrading the graphical interface's experience (the "regenerate" action).

## Reusable `mazegen` module

All of the generation logic is isolated in the `mazegen` package, installable independently of the graphical interface, and designed to be reused in a future project.

### Installation

```bash
pip install mazegen-<version>-py3-none-any.whl --break-system-packages
# or, for development, from the src folder:
cd src && pip install -e . --break-system-packages
```

### Basic usage

The simplest way to use the module is through the `MazeGenerator` orchestrator, which selects the right engine (DFS or Prim) automatically from the configuration:

```python
from mazegen import MazeGenerator

# From a KEY=VALUE configuration file
generator = MazeGenerator.from_config("config.txt")
generator.generate()
generator.export()  # writes the grid + entry/exit + solution to OUTPUT_FILE
```

For finer control, the lower-level building blocks (`Config`, `TxtWriter`, `PrimGenerator`/`DfsGenerator`, `BfsSolver`) remain accessible directly:

```python
from mazegen import Config, TxtWriter, PrimGenerator, BfsSolver

# 1. Load a configuration (KEY=VALUE text file)
cfg = Config.from_file("config.txt")

# 2. Instantiate the generator with a writer
writer = TxtWriter()
generator = PrimGenerator(cfg, writer)

# 3. Generate the maze
generator.generate()

# 4. Export to the file defined in the configuration (grid + entry/exit + solution)
generator.export()
```

### Passing custom parameters (size, seed…)

Parameters (`WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `PERFECT`, `SEED`, `ALGORITHM`…) can come from a configuration file (`Config.from_file`) or be passed directly as keyword arguments (`Config.from_params`, or directly to `MazeGenerator`). The `seed` guarantees reproducibility: two runs with the same configuration and the same seed produce exactly the same maze.

```python
# From a file
cfg = Config.from_file("my_config.txt")
print(cfg.width, cfg.height, cfg.seed, cfg.perfect)

# Or directly from parameters, via MazeGenerator
generator = MazeGenerator(
    width=20, height=20,
    entry=(0, 0), exit_pos=(19, 19),
    seed=42, perfect=True, algorithm="dfs",
    output_file="maze.txt",
)
```

### Accessing the generated structure and the solution

```python
# With a low-level generator (PrimGenerator/DfsGenerator):
# The grid: a list of lists of integers (wall bitmask per cell)
grid = generator.maze

# The solution: shortest path between entry and exit (coordinates + literal path)
solver = BfsSolver()
path_coords, path_letters = solver.solve(grid, cfg.entry_pt, cfg.exit_pt)
# generator.solution returns the same (path_coords, path_letters) tuple, cached

# With the MazeGenerator orchestrator, the same data is available via:
grid = mg.get_grid()          # list[list[int]]
path_coords = mg.get_solution()  # list[tuple[int, int]]
```

> ℹ️ **Note**: the structure exposed via `maze`/`get_grid()` (a list of lists of integers) is not necessarily identical to the output file's text format — it is designed to be manipulated directly in memory by a future project.

## Graphical interface controls

| Key | Action |
|---|---|
| `R` | Regenerates a new maze (new configuration/seed) and redisplays it. |
| `P` | Shows/hides the shortest path between entry and exit. |
| `C` | Changes the wall color (cycles through a color palette). |
| `Esc` | Quits the program. |

The window also displays the entry (green), the exit (red), the "42" pattern (dedicated cells) and, when enabled, the solution path (yellow).

## Team and project management

### Roles

- **Alexandrô / arakotot** — front end, mlx rendering, fix CFUNCTYPE, ...
- **Rolland / mamiandr** — mazegenerator parts, installable package, algorithm and data validation ...

### Planning

Our schedule was quite tight. We defined everyone's tasks beforehand and set strict timelines for the project's progress. Specifically, arakotot stayed on campus on Mondays and worked on the project every afternoon, while mamiandr completed his share every morning from 5:00 AM to 9:00 AM. Fridays were reserved for meetings, progress reporting, and weekly check-ins. We used this time to share our research findings and align on the next steps.

The main weakness of our planning was that we had very little time for peer learning, as our schedules only overlapped on Fridays. If we were to do it differently, we would create a schedule that incorporates more peer learning.

### Retrospective

- **What went well**: infrastructure - config parser, gui - Maze loader
- **What could be improved**: ASCII terminal rendering in addition to the MLX rendering

### Tools used

- **Poetry** for dependency management and packaging of the `mazegen` module.
- **Pydantic** for strict validation of the configuration file.
- **flake8** / **mypy** for style compliance and static typing.
- **MiniLibX (MLX)** for the graphical display.

## Bonuses

- Two generation algorithms available (Prim, DFS), selectable via the `ALGORITHM` key.
- generation animation
- path finding animation

## Resources

### Documentation and references

- [Prim's algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [Maze generation algorithms (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Poetry documentation](https://python-poetry.org/docs/)
- [MiniLibX documentation (42)](https://harm-smits.github.io/42docs/libs/minilibx)

### Use of AI

*In this project, AI was used for generating docstrings and the README, debugging, fixing mypy issues, and researching topics such as DFS algorithms. It proved to be an indispensable partner in completing this project.*
