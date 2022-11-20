from datetime import datetime, timedelta
from typing import List, Union


class Result:
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