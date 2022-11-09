from abc import ABC, abstractmethod
from typing import List

from result import Result


class ITimerImporter(ABC):

    @abstractmethod
    def load_all(self) -> List[Result]:
        raise NotImplementedError

