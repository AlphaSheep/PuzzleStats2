from datetime import datetime, timedelta


class Result:
    def __init__(self, start: datetime, result: timedelta, category: str, penalty: timedelta, source: str) -> None:
        self.start: datetime = start
        self.result: timedelta = result
        self.category: str = category
        self.penalty: timedelta = penalty
        self.source: str = source

    def __repr__(self) -> str:
        return f"{self.category}: {self.result} . {self.start.strftime('%c')} ({self.source})"
