from abc import ABC, abstractmethod
from typing import List, Dict, Set

from result import Result


class ITimerImporter(ABC):

    def __init__(self) -> None:
        self.results: List[Result] = []
        self.categories: Set[str] = set()
        self.dnf_counts: Dict[str, int] = {}

    def reset(self) -> None:
        self.__init__()

    @abstractmethod
    def import_all(self) -> None:
        raise NotImplementedError
