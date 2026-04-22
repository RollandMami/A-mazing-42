import os
from typing import Dict, List, Any
from abc import ABC, abstractmethod

class ConfigError(Exception):
    pass


class ConfigLoader(ABC):
    @abstractmethod
    def load(self, path: str) -> Dict[str, str]:
        pass


class TxtLoader(ConfigLoader):
    def load(self, path: str) -> Dict[str, str]:
        parsed_data: Dict[str, str] = {}
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(f"line_{line_num}::Bad syntax,  file must contain one ‘KEY=VALUE‘ pair per line")
                key, value = [part.strip() for part in line.split("=", 1)]
                parsed_data[key] = value
        return parsed_data


class Config:
    """ce class permet de recuperer les info utiles
    pour la generation du map gan generator"""
    REQUIRED = [
        "WIDTH", "HEIGHT", "ENTRY",
        "EXIT", "OUTPUT_FILE", "PERFECT"
        ]
    OPTIONAL = ["SEED", "ALGORITHM", "DISPLAY_MODE"]

    def __init__(self, cfg_path: str, loader: ConfigLoader = TxtLoader()) -> None:
        self._path: str = cfg_path
        self._data: Dict[str, Any] = self._parse_file(loader)
        

    @property
    def path(self) -> str: return self._path

    @property
    def width(self) -> int: return self._data.get("WIDTH")

    @property
    def height(self) -> int: return self._data.get("HEIGHT")

    @property
    def entry_pt(self) -> tuple: return self._data.get("ENTRY")

    @property
    def exit_pt(self) -> tuple: return self._data.get("EXIT")

    @property
    def output_file(self) -> str: return self._data.get("OUTPUT_FILE")

    @property
    def perfect(self) -> bool: return self._data.get("PERFECT")

    @property
    def seed(self) -> int: return self._data.get("SEED", 0)

    @property
    def algorithm(self) -> str: return self._data.get("ALGORITHM", "DFS")

    @staticmethod
    def configuration_validator(file_path: str, loader: ConfigLoader) -> Dict[str, str]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le fichier {file_path} est introuvable.")
        #if not file_path.endswith(".txt"):
        #    raise ConfigError("Le fichier de configuration doit être un .txt")
        parsed_data: Dict[str, str] = loader.load(file_path)
        for key in parsed_data:
            if key not in Config.REQUIRED and key not in Config.OPTIONAL:
                    raise ConfigError(f"Unknown key: {key}")
        missing: List[str] = [key for key in Config.REQUIRED if key not in parsed_data]
        if missing:
            raise ConfigError(f"missing keyword {' :: '.join(missing)}")
        # validation values:
        Config._value_validator(parsed_data)
        return parsed_data

    @staticmethod
    def _value_validator(data: Dict[str, str]) -> bool:
        """ Verifier la coherence mathématique des donnée """
        try:
            w, h = int(data["WIDTH"]), int(data["HEIGHT"])
            if w <= 0 or h <= 0:
                raise ConfigError(f"Impossible maze parameter >> width({w}) or height({h}) must be positif number")
            for key in ["ENTRY", "EXIT"]:
                coords = [int(c) for c in data[key].split(",")]
                if len(coords) != 2:
                    raise ValueError(f"{key}: value must be positive couple of like (x, y)")
                x, y = coords
                if  not (0 <= x < w and 0 <= y < h):
                    raise ConfigError(f"Impossible maze parameter:\n\t{key} ({x},{y}) est hors limites ({w}x{h})")
            out_file: str = data["OUTPUT_FILE"]
            if not out_file.endswith(".txt") or any(sep in out_file for sep in [" ", "\t", "\n", "\r"]):
                raise ValueError("Output_file must be txt format, and not include separator")
            if "SEED" in data:
                float(data["SEED"])
            if data["PERFECT"] not in ["True", "False"]:
                raise ValueError("PERFECT key must handle boolean field like True or False")
        except ValueError as e:
            raise ConfigError(f"Data type error : {e}")
        return True

    def _parse_file(self, loader: ConfigLoader) -> Dict[str, Any]:
        raw: Dict[str, str] = Config.configuration_validator(self.path, loader)
        final: Dict[str, Any] = {}
        for k, v in raw.items():
            if k in ["WIDTH", "HEIGHT", "SEED"]:
                final[k] = int(v)
            elif k in ["ENTRY", "EXIT"]:
                final[k] = tuple(int(c) for c in v.split(","))
            elif k == "PERFECT":
                final[k] = (v.lower() == "true")
            else:
                final[k] = v
        return final
