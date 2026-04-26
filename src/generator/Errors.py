class MazeError(Exception):
    """Classe de base pour les erreurs du projet"""
    pass


class GenerationError(MazeError):
    """Erreur spécifique à l'algorithme de génération"""
    pass
