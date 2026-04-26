from typing import Dict
from abc import ABC, abstractmethod
from . import ConfigError


class ConfigLoader(ABC):
    @abstractmethod
    def load(self, path: str) -> Dict[str, str]:
        pass


class TxtLoader(ConfigLoader):
    def load(self, path: str) -> Dict[str, str]:
        if not path.endswith(".txt"):
            raise ConfigError("Le fichier de configuration doit être un .txt")
        parsed_data: Dict[str, str] = {}
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(f"line_{line_num}::Bad syntax,  file \
must contain one ‘KEY=VALUE‘ pair per line")
                key, value = [part.strip() for part in line.split("=", 1)]
                parsed_data[key] = value
        return parsed_data
