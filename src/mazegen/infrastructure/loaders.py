from typing import Dict
from abc import ABC, abstractmethod
from .Errors import ConfigError
from pathlib import Path


MAX_LINES = 1000  # Sécurité for unsecured files


class ConfigLoader(ABC):
    """Abstract base class for configuration file loaders.

    Defines the contract for reading raw key-value pairs from different
    configuration file formats.
    """

    @abstractmethod
    def load(self, path: str) -> Dict[str, str]:
        """Loads and parses raw key-value pairs from a configuration file.
        Args:
            path (str): File path to load.
        Returns:
            Dict[str, str]: A dictionary containing key-value pairs
            extracted from the file.
        Raises:
            ConfigError: If the file format, extension, or content is invalid.
            FileNotFoundError: If the target file does not exist.
        """
        ...


class TxtLoader(ConfigLoader):
    """Loader strategy for key-value pair `.txt` configuration files."""
    def load(self, path: str) -> Dict[str, str]:
        """Parses a `.txt` file formatted with `KEY=VALUE` pairs line by line.
        Empty lines and lines starting with `#` (comments) are ignored.
        Args:
            path (str): Path to the target `.txt` configuration file.
        Returns:
            Dict[str, str]: Dictionary mapping raw string
            keys to string values.
        Raises:
            ConfigError: If the extension is not `.txt`, the file exceeds
                `MAX_LINES`, or any line fails the `KEY=VALUE` syntax.
            FileNotFoundError: If the file at `path` does not exist.
        """
        v = Path(path)
        if v.is_dir():
            raise ConfigError(
                "Do not use directory please!!! Use <config.txt> instead")
        if not path.endswith(".txt"):
            raise ConfigError("config file must end with '.txt' extention")
        parsed_data: Dict[str, str] = {}
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if line_num > MAX_LINES:
                    raise ConfigError("File exceeds max limit({MAX_LINES})")
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    msg1 = f"line_{line_num}::Bad syntax,\n"
                    msg2 = "file must contain one ‘KEY=VALUE‘ pair per line"
                    raise ConfigError(msg1 + msg2)
                if "#" in line:
                    msg1 = f"line_{line_num} <{line}> Bad syntax,\n"
                    raise ConfigError(msg1 + "Inline comment forbidden")
                key, value = [part.strip() for part in line.split("=", 1)]
                parsed_data[key.upper()] = value
        return parsed_data
