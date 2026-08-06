from abc import ABC, abstractmethod
from typing import List


class BaseWriter(ABC):
    """Abstract interface defining file export operations for
    generated mazes."""

    @abstractmethod
    def write(self, maze: List[List[int]], destination: str) -> None:
        """Writes the maze grid data to a destination file.
        Args:
            maze (List[List[int]]): 2D grid containing cell
            wall bitmask integers.
            destination (str): Target file path.
        Raises:
            IOError: If an error occurs during file writing.
        """
        ...

    @abstractmethod
    def insert(self, txt: str, destination: str) -> None:
        """Appends additional text content to a destination file.

        Args:
            txt (str): Text string to append.
            destination (str): Target file path.

        Raises:
            IOError: If an error occurs during file writing.
        """
        ...


class TxtWriter(BaseWriter):
    """Writer implementation for exporting mazes in hexadecimal text format."""
    def write(self, maze: List[List[int]], destination: str) -> None:
        """Exports a 2D maze grid as hexadecimal character rows into a file.

        Each integer cell bitmask is converted to its uppercase
        hexadecimal representation.

        Args:
            maze (List[List[int]]): 2D grid of cell wall bitmask integers.
            destination (str): Target file path.

        Raises:
            IOError: If writing to the file fails.
        """
        try:
            content: str = "\n".join(
                "".join(f"{cell:X}" for cell in row) for row in maze
            )
            with open(destination, 'w') as f:
                f.write(content + "\n")
            print(
                f"Succès : '{maze[0][:4]}...' exported in {destination}")
        except IOError as e:
            print(f"Erreur while writing file : {e}")

    def insert(self, txt: str, destination: str) -> None:
        """Appends a line of text to an existing file.

        Args:
            txt (str): Text string to append.
            destination (str): Target file path.

        Raises:
            IOError: If appending to the file fails.
        """
        try:
            with open(destination, 'a') as f:
                f.write(str(txt) + "\n")
            print(f"Succès : {txt.strip()[:6]}... exported in {destination}")
        except IOError as e:
            print(f"Erreur  while writing file : {e}")
