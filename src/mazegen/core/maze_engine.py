from typing import Optional
from ..infrastructure.config_parser import Config
from ..infrastructure.writers import TxtWriter
from ..generator import PrimGenerator, BaseGen, DfsGenerator


class MazeGenerator:
    """Orchestrator class responsible for maze generation workflow.

    Acts as the primary public API for the package. It handles configuration
    initialization, dynamically instantiates the requested generation engine
    (e.g., DFS, Prim), triggers maze generation, and manages export tasks.

    Args:
        width (int, optional): Maze grid width. Defaults to 15.
        height (int, optional): Maze grid height. Defaults to 15.
        entry (Tuple[int, int], optional): Entry point coordinates (x, y).
            Defaults to (0, 0).
        exit_pos (Tuple[int, int], optional): Exit point coordinates (x, y).
            Defaults to (14, 14).
        seed (Optional[int], optional): Random seed for
        generation reproducibility.
            Defaults to None.
        perfect (bool, optional): If True, generates a perfect
        maze without loops.
            Defaults to True.
        algorithm (str, optional): Generation algorithm name
        or key (e.g., "dfs", "prim").
            Defaults to "dfs".
        output_file (str, optional): Destination path for
        exporting the maze file.
            Defaults to "output.txt".

    Raises:
        ConfigError: If configuration parameter validation fails.
        KeyError: If the resolved algorithm ID does not
        match a registered engine.
    """
    _ENGINES: dict[int, type[BaseGen]] = {
        0: DfsGenerator,   # AlgorithmEnum.DFS
        1: PrimGenerator,  # AlgorithmEnum.PRIM
    }

    def __init__(
        self,
        width: int = 15,
        height: int = 15,
        entry: tuple[int, int] = (0, 0),
        exit_pos: tuple[int, int] = (14, 14),
        seed: Optional[int] = None,
        perfect: bool = True,
        algorithm: str = "dfs",
        output_file: str = "output.txt",
    ) -> None:
        cfg = Config.from_params(
            width=width, height=height, entry=entry, exit=exit_pos,
            seed=seed, perfect=perfect, algorithm=algorithm,
            output_file=output_file,
        )
        self._build_engine(cfg)

    @classmethod
    def from_config(cls, config_path: str) -> "MazeGenerator":
        """Factory method to instantiate `MazeGenerator`
        from a configuration file.

        Args:
            config_path (str): Path to the configuration file (e.g., `.txt`).

        Returns:
            MazeGenerator: An initialized instance of `MazeGenerator`.

        Raises:
            FileNotFoundError: If `config_path` does not exist.
            ConfigError: If file content parsing or validation fails.
        """
        instance = cls.__new__(cls)
        instance._build_engine(Config.from_file(config_path))
        return instance

    def _build_engine(self, cfg: Config) -> None:
        """Instantiates the concrete generation engine
        specified by configuration.

        Args:
            cfg (Config): Validated configuration object.

        Raises:
            KeyError: If `cfg.algorithm` is not mapped in `_ENGINES`.
        """
        engine_cls = self._ENGINES[cfg.algorithm]
        self._engine: BaseGen = engine_cls(cfg, TxtWriter())

    def generate(self) -> None:
        """Triggers the execution of the selected maze generation algorithm."""
        self._engine.generate()

    def get_grid(self) -> list[list[int]]:
        """Retrieves the generated 2D maze grid.

        Returns:
            List[List[int]]: 2D grid containing cell wall bitmask integers.
        """
        return self._engine.maze

    def get_solution(self) -> list[tuple[int, int]]:
        """Retrieves the solution path from entry to exit.

        Returns:
            List[Tuple[int, int]]: Ordered list of (x, y) coordinates forming
                the solution path, or an empty list if no solution exists.
        """
        sol = self._engine.solution
        return sol[0] if sol else []

    def export(self) -> None:
        """Exports the generated maze to the configured output file."""
        self._engine.export()

    @property
    def width(self) -> int:
        """int: Width of the maze grid."""
        return self._engine.width

    @property
    def height(self) -> int:
        """int: Height of the maze grid."""
        return self._engine.height

    @property
    def entry(self) -> tuple[int, int]:
        """Tuple[int, int]: Entry point (x, y) coordinates."""
        return self._engine.entry

    @property
    def exit_pos(self) -> tuple[int, int]:
        """Tuple[int, int]: Exit point (x, y) coordinates."""
        return self._engine.exit

    @property
    def mask_42(self) -> Optional[list[tuple[int, int]]]:
        """Optional[List[Tuple[int, int]]]: Mask pattern
        coordinates if active, otherwise None."""
        return self._engine.mask_42

    @property
    def output_file(self) -> str:
        """str: Destination output file path."""
        return self._engine.output_file
