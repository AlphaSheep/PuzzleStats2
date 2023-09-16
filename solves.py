from datetime import datetime, timedelta
from typing import List, Union, Dict

from pandas import DataFrame, Series


class Solve:
    def __init__(self, start: datetime, result: timedelta, category: str, penalty: timedelta, source: str) -> None:
        self.start: datetime = start
        self.result: timedelta = result
        self.category: str = category
        self.penalty: timedelta = penalty
        self.source: str = source

    def __repr__(self) -> str:
        return f"{self.category}: {self.result} . {self.start.strftime('%c')} ({self.source})"

    def as_list(self) -> List[Union[datetime, timedelta, str]]:
        return [self.start, self.result, self.category, self.penalty, self.source]

    def as_dict(self) -> Dict[str, Union[datetime, timedelta, str]]:
        return {
            "start": self.start,
            "result": self.result,
            "category": self.category,
            "penalty": self.penalty,
            "source": self.source
        }


class SolveCollection(list):

    def as_dataframe(self) -> DataFrame:
        return DataFrame([solve.as_dict() for solve in self])

    def as_timeseries(self) -> Series:
        return Series({solve.start: solve.result for solve in self})
