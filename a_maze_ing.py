import sys
import os
from gui.window import Window

# Ajouter le repertoire src/ au path pour les imports internes
_src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

print(sys.executable)


def main() -> None:
    window = Window()

    # Charger le labyrinthe initial depuis le fichier maze.txt
    window.load_initial_maze("maze.txt")

    window.run()


if __name__ == "__main__":
    main()
