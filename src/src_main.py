import sys
from core import MazeGenerator


if len(sys.argv) < 2:
    print("Usage: python maze_engine.py <config_file>")
else:
    try:
        config_file: str = sys.argv[1]
        orchestrator: MazeGenerator = MazeGenerator(config_file)
        orchestrator.run()
    except Exception as e:
        print(e)