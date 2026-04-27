from infrastructure.config_parser import Config
from infrastructure.writers import TxtWriter
from generator import PrimGenerator, DfsGenerator, BaseGen


class MazeGenerator:
    """
    The Orchestrator. 
    It reads config, selects the algorithm, and triggers export.
    """
    def __init__(self, config_path: str) -> None:
        # 1. Parse the configuration file
        self.parser: Config = Config(config_path)
        # 2. Setup the writer
        self.writer: TxtWriter = TxtWriter()
        # 3. Choose the generator (Strategy Pattern)
        # Tu pourras ajouter un IF ici plus tard pour choisir entre DFS et Prim
        self.engine: BaseGen = PrimGenerator(self.parser, self.writer)

    def run(self) -> None:
        """Executes the generation and export process."""
        print(f"Generating maze using Prim's algorithm...")
        self.engine.generate()
        print(f"Exporting to {self.parser.output_file}...")
        self.engine.export()
        print("Done!")
