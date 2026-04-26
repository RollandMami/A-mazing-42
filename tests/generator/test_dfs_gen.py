from generator import Dfs_generator, TxtWriter, GenerationError
import pytest


class MockConfig:
    """Un faux objet Config pour les tests"""
    def __init__(self):
        self.width = 10
        self.height = 10
        self.entry_pt = (0, 0)
        self.exit_pt = (9, 9)
        self.output_file = "test_maze.txt"
        self.perfect = True
        self.seed = 42


def test_maze_dimensions():
    """Vérifie que la matrice a la bonne taille [Y][X]"""
    cfg = MockConfig()
    gen = Dfs_generator(cfg, TxtWriter())
    # Rappel : maze[y][x] donc len(maze) est la hauteur
    assert len(gen.maze) == 10
    assert len(gen.maze[0]) == 10


def test_generation_fills_visited():
    """Vérifie que l'algorithme casse bien des murs"""
    cfg = MockConfig()
    gen = Dfs_generator(cfg, TxtWriter())
    gen.generate()
    # On vérifie qu'au moins une cellule n'est plus à 15 (mur plein)
    flatten_maze = [cell for row in gen.maze for cell in row]
    assert any(cell < 15 for cell in flatten_maze)


def test_seed_reproducibility():
    """Vérifie que le même seed produit le même labyrinthe"""
    cfg = MockConfig()
    gen1 = Dfs_generator(cfg, TxtWriter())
    gen2 = Dfs_generator(cfg, TxtWriter())
    gen1.generate()
    gen2.generate()
    assert gen1.maze == gen2.maze


def test_invalid_width_raises_error():
    """Vérifie que le générateur lève une erreur si la largeur est invalide"""
    cfg = MockConfig()
    cfg.width = 0  # Valeur qui déclenche ton raise dans generate()
    gen = Dfs_generator(cfg, TxtWriter())
    # On utilise pytest.raises pour intercepter l'exception attendue
    with pytest.raises(GenerationError):
        gen.generate()
