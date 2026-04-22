import pytest
import os
from infrastructure import Config, ConfigError


# 1. Test d'un succès (Chemin nominal)
def test_config_valid_file():
    # On initialise la config
    cfg = Config("config.txt")

    # On vérifie les valeurs
    assert cfg.width == 20
    assert cfg.height == 15
    assert cfg.entry_pt == (0, 0)
    assert isinstance(cfg.perfect, bool)
    assert cfg.perfect is True

# 2. Test d'un fichier introuvable
def test_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        Config("un_fichier_qui_n_existe_pas.txt")

# 3. Test d'une erreur de syntaxe (le "=" manquant)
def test_config_bad_syntax(tmp_path):
    cfg_file = tmp_path / "bad_syntax.txt"
    cfg_file.write_text("WIDTH 10\n") # Erreur ici : pas de '='

    with pytest.raises(ConfigError) as excinfo:
        Config(str(cfg_file))
    assert "Bad syntax" in str(excinfo.value)

# 4. Test des limites (Coordonnées hors grille)
def test_config_out_of_bounds(tmp_path):
    cfg_file = tmp_path / "bounds.txt"
    content = (
        "WIDTH=5\nHEIGHT=5\nENTRY=10,10\n" # 10,10 est hors d'une grille 5x5
        "EXIT=1,1\nPERFECT=True\nOUTPUT_FILE=m.txt"
    )
    cfg_file.write_text(content)

    with pytest.raises(ConfigError):
        Config(str(cfg_file))