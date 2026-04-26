from abc import ABC, abstractmethod
from typing import List


class BaseWriter(ABC):
    @abstractmethod
    def write(self, maze: List[List[int]], destination: str) -> None:
        """Méthode pour écrire le labyrinthe sur un support donné"""
        pass


class TxtWriter(BaseWriter):
    def write(self, maze: List[List[int]], destination: str) -> None:
        try:
            with open(destination, 'a') as f:
                for row in maze:
                    line = "".join(format(cell, 'X') for cell in row)
                    f.write(line + "\n")
            print(f"Succès : Labyrinthe exporté dans {destination}")
        except IOError as e:
            print(f"Erreur lors de l'écriture du fichier : {e}")

