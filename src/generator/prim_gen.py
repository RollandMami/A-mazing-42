from infrastructure import Config, BaseWriter
import random
from typing import List, Tuple, Set
from . import GenerationError, Base_Gen


class Prim_Gen(Base_Gen):
    def __init__(self, cfg: Config, writer: BaseWriter) -> None:
        super().__init__(cfg, writer)

    def generate(self) -> None:
        pass
