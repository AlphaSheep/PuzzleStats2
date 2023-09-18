from abc import ABC, abstractmethod
from typing import List, Dict, Set, Union, Any

from solves import Solve, SolveCollection


class BaseTimerImporter(ABC):

    def __init__(self) -> None:
        self.solves: SolveCollection = SolveCollection()
        self.categories: Set[str] = set()
        self.dnf_counts: Dict[str, int] = {}

        self.category_config: Union[List[str], Dict[str, str]]
        self.move_categories: List[str] = []
        self.multi_categories: List[str] = []

        self.additional_data: Dict[str, Any] = {}

        self.folder: str = ""
        self.pattern: str = ""
        self.files: List[str] = []

    def reset(self) -> None:
        self.solves = SolveCollection()
        self.categories = set()
        self.dnf_counts = {}

    @abstractmethod
    def import_all(self) -> None:
        raise NotImplementedError
