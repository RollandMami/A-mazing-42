import sys
from .core import MazeGenerator


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python maze_engine.py <config_file>")
    else:
        try:
            config_file: str = sys.argv[1]
            orchestrator: MazeGenerator = MazeGenerator(config_file)
            orchestrator.run()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
