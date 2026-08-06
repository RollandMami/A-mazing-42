*This project has been created as part of the 42 curriculum by mamiandr[, <login2>[, <login3>]].*

# A-Maze-ing 🌀

> *"This is the way"* — A Python maze generator, with hexadecimal-encoded export, automatic solving, and an interactive graphical display (MiniLibX).

---

## Table of Contents

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
- [Reusable `mazegen` module](#reusable-mazegen-module)
- [Graphical interface controls](#graphical-interface-controls)
- [Team and project management](#team-and-project-management)
- [Bonuses](#bonuses)
- [Resources](#resources)

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
│       ├── __init__.py       # Exposes the package's public API
│       ├── mazegen_main.py   # CLI orchestration (entry point of the `maze-gen` script)
│       ├── core/
│       │   └── maze_engine.py   # `MazeGenerator`: orchestrator (config → generation → export)
│       ├── infrastructure/
│       │   ├── config_parser.py # `Config` + Pydantic validation of the config file
│       │   ├── loaders.py       # Parsing of the `KEY=VALUE` config file
│       │   ├── writers.py       # Writing of the output file (hexadecimal grid)
│       │   └── Errors.py
│       ├── generator/
│       │   ├── base_gen.py      # `BaseGen`: abstract class ("42" mask, imperfections, export)
│       │   ├── prim_gen.py      # `PrimGenerator`: generation using Prim's algorithm
│       │   ├── dfs_gen.py       # `DfsGenerator`: generation via depth-first search (DFS)
│       │   └── Errors.py
│       └── solver/
│           ├── base_solver.py
│           ├── bfs_solver.py    # `BfsSolver`: shortest path (BFS)
│           └── astar_solver.py  # (reserved for a future A* implementation)
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
| `SEED` | optional | Random seed for reproducibility. If omitted, a random seed is generated. | `SEED=42` |
| `ALGORITHM` | optional | Generation algorithm: `1` = DFS, `2` = Prim, `3` = A* *(reserved)*. | `ALGORITHM=2` |
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

**Primary algorithm: randomized Prim's algorithm** (`PrimGenerator`).

Principle:
1. Start from a random cell, added to the set of "visited" cells.
2. All of its neighbors are added to a list of "frontier" cells.
3. While there are frontier cells left: pick one at random, connect it to one of its already-visited neighbors (breaking the corresponding wall on both sides, to guarantee consistency between neighboring cells), then add it to the visited set and expand the frontier list.
4. If `PERFECT=False`, an additional pass randomly breaks ~10% of the internal walls (excluding the "42" pattern) to create loops.

A second algorithm, **DFS / recursive backtracker** (`DfsGenerator`), is also implemented and selectable via the `ALGORITHM` key in the configuration file.

### Why this algorithm?

**Prim's algorithm** was chosen as the default because:

- it produces mazes with **many short branches** rather than long winding corridors (unlike DFS, which tends to generate long dead ends) — resulting in a more "organic" visual look, closer to a real-world maze.
- it fits naturally with our **protected-mask** logic (the "42" pattern): it is enough to exclude certain cells from the frontier list to guarantee they are never connected to the rest of the maze other than along their outline.
- its complexity remains reasonable (roughly `O(cells × 4)` thanks to the frontier structure), which allows large grids to be generated quickly without degrading the graphical interface's experience (the "regenerate" action).

**DFS** remains available as an alternative: simpler to implement and understand, it generates mazes with longer corridors and fewer branches, useful for comparing the two approaches.

## Reusable `mazegen` module

All of the generation logic is isolated in the `mazegen` package, installable independently of the graphical interface, and designed to be reused in a future project.

### Installation

```bash
pip install mazegen-<version>-py3-none-any.whl --break-system-packages
# or, for development, from the src folder:
cd src && pip install -e . --break-system-packages
```

### Basic usage

```python
from mazegen import Config, TxtWriter, PrimGenerator, BfsSolver

# 1. Load a configuration (KEY=VALUE text file)
cfg = Config("config.txt")

# 2. Instantiate the generator with a writer
writer = TxtWriter()
generator = PrimGenerator(cfg, writer)

# 3. Generate the maze
generator.generate()

# 4. Export to the file defined in the configuration (grid + entry/exit + solution)
generator.export()
```

### Passing custom parameters (size, seed…)

Parameters (`WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `PERFECT`, `SEED`, `ALGORITHM`…) are defined in the configuration file loaded by `Config`. The `seed` guarantees reproducibility: two runs with the same configuration and the same seed produce exactly the same maze.

```python
cfg = Config("my_config.txt")
print(cfg.width, cfg.height, cfg.seed, cfg.perfect)
```

### Accessing the generated structure and the solution

```python
# The grid: a list of lists of integers (wall bitmask per cell)
grid = generator.maze

# The solution: shortest path between entry and exit (coordinates + literal path)
solver = BfsSolver()
path_coords, path_letters = solver.solve(grid, cfg.entry_pt, cfg.exit_pt)
```

> ℹ️ **Note**: the structure exposed via `generator.maze` (a list of lists of integers) is not necessarily identical to the output file's text format — it is designed to be manipulated directly in memory by a future project.

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

*(to be completed — e.g. generation/algorithms, infrastructure/config, solver, MLX display, packaging & linting)*

- **[Name / login]** — …
- **[Name / login]** — …

### Planning

*(to be completed — organization planned at the start of the project, deviations observed and adjustments made along the way)*

### Retrospective

- **What went well**: *(to be completed)*
- **What could be improved**: *(to be completed — e.g. dynamic algorithm selection via `ALGORITHM` to be wired into `MazeGenerator`, implementation of the A* solver, ASCII terminal rendering in addition to the MLX rendering)*

### Tools used

- **Poetry** for dependency management and packaging of the `mazegen` module.
- **Pydantic** for strict validation of the configuration file.
- **flake8** / **mypy** for style compliance and static typing.
- **MiniLibX (MLX)** for the graphical display.
- *(complete with any other tools used: editor, CI, etc.)*

## Bonuses

- Two generation algorithms available (Prim, DFS), selectable via the `ALGORITHM` key.
- *(complete if other bonuses were implemented, e.g. generation animation, ASCII display mode, dedicated coloring of the "42" pattern…)*

## Resources

### Documentation and references

- [Prim's algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [Maze generation algorithms (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Poetry documentation](https://python-poetry.org/docs/)
- [MiniLibX documentation (42)](https://harm-smits.github.io/42docs/libs/minilibx)

### Use of AI

*(to be completed precisely: for which tasks and on which parts of the project AI was used — e.g. help structuring the configuration parsing with Pydantic, review of the BFS solver, generation of this README from the existing code, etc. Every AI-generated suggestion was reviewed, tested, and discussed with a peer before being integrated, in accordance with the subject's guidelines.)*