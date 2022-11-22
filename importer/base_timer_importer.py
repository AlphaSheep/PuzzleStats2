from abc import ABC, abstractmethod
from typing import List, Dict, Set, Union, Any

from result import Result


class BaseTimerImporter(ABC):

    def __init__(self) -> None:
        self.results: List[Result] = []
        self.categories: Set[str] = set()
        self.dnf_counts: Dict[str, int] = {}

        self.category_config: Union[List[str], Dict[str, str]]

        self.additional_data: Dict[str, Any] = {}

    def reset(self) -> None:
        self.results = []
        self.categories = set()
        self.dnf_counts = {}

    @abstractmethod
    def import_all(self) -> None:
        raise NotImplementedError
