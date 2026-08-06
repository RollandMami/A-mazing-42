"""Entry point module for the Maze Engine GUI application.

This script parses command-line arguments to locate the
maze configuration file, initializes the main window interface,
loads the initial maze layout, and runs the interactive display loop.
"""

import sys
import os
from gui.window import Window
try:
    from mazegen import Config, ConfigError
except ModuleNotFoundError:
    print("Use the command : make run")

# add src folder for internal imports
_src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)


def main() -> None:
    """Parses command-line arguments and runs the Maze application loop.

    Expects the configuration file path as the first positional argument.
    Initializes the Window instance, loads the maze file,
    and starts the event loop.

    Raises:
        Exception: Catches and logs any unexpected runtime
        errors during execution.
    """
    if len(sys.argv) < 2:
        print("Usage: python maze_engine.py <config_file>")
        sys.exit(1)
    config_file: str = sys.argv[1]
    try:
        Config.from_file(config_file)
    except ConfigError as e:
        print(f"Config file error: {e}")
        sys.exit(1)
    except (FileNotFoundError, OSError) as e:
        print(f"Cannot read config file: {e}")
        sys.exit(1)
    try:
        window = Window()
        if not window.regenerate_maze(config_file):
            print("Failed to generate the initial maze.")
            sys.exit(1)
        window.run()
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
