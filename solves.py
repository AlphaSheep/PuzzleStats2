from typing import List, Union, Dict, Optional, Tuple, Final

from datetime import datetime, timedelta
from pandas import DataFrame, Series


_ZERO_TIME: Final[datetime] = datetime.strptime('00:00.00', '%M:%S.%f')


def _time_to_str(time: timedelta, decimals = 3) -> str:
    if decimals == 2:
        time += timedelta(microseconds=4999)
    timestr = (_ZERO_TIME + time).strftime('%M:%S.%f')[:-(6-decimals)]
    return timestr.lstrip('0:')


class Result:

    def __init__(self, value: timedelta | int | float | Tuple[int, int, timedelta] | None = None) -> None:
        self.value: timedelta | int | float | Tuple[int, int, timedelta] | None = value

    def __float__(self) -> float:
        if self.value is None:
            return float('NaN')
        elif isinstance(self.value, int) or isinstance(self.value, float):
            # Fewest moves
            return float(self.value)
        elif isinstance(self.value, tuple):
            # Multiple blindfolded
            solved = self.value[0]
            attempted = self.value[1]
            seconds = int(self.value[2].total_seconds()) * 100
            missed = attempted - solved
            difference = (99 - solved - missed) * 1000000
            return difference + seconds + missed
        else:
            # Standard timed speedsolve
            return self.value.total_seconds()

    def __add__(self, other: 'Result') -> 'Result':
        if self.value is None:
            # Special case to allow adding to a zero result
            return other
        if isinstance(self.value, int) or isinstance(self.value, float):
            # Fewest moves
            assert isinstance(other.value, int) or isinstance(other.value, float), "Fewest moves result can only be added to another fewest moves result"
            return Result(self.value + other.value)
        elif isinstance(self.value, tuple):\
            # Multiple blindfolded
            assert isinstance(other.value, tuple), "Multiple blindfolded result can only be added to another multiple blindfolded result"
            solved = self.value[0] + other.value[0]
            attempted = self.value[1] + other.value[1]
            time = self.value[2] + other.value[2]
            return Result((solved, attempted, time))
        else:
            assert isinstance(other.value, timedelta), "Timed speedsolve result can only be added to another timed speedsolve result"
            return Result(self.value + other.value)

    def __sub__(self, other: 'Result') -> 'Result':
        if self.value is None:
            raise ValueError("Cannot subtract from a zero result")
        elif other.value is None:
            return Result(self.value)
        elif isinstance(self.value, int) or isinstance(self.value, float):
            assert isinstance(other.value, int) or isinstance(other.value, float), "Fewest moves result can only be subtracted from another fewest moves result"
            return Result(self.value - other.value)
        elif isinstance(self.value, tuple):
            assert isinstance(other.value, tuple), "Multiple blindfolded result can only be subtracted from another multiple blindfolded result"
            solved = self.value[0] - other.value[0]
            attempted = self.value[1] - other.value[1]
            time = self.value[2] - other.value[2]
            return Result((solved, attempted, time))
        else:
            assert isinstance(other.value, timedelta), "Timed speedsolve result can only be subtracted from another timed speedsolve result"
            return Result(self.value - other.value)

    def __truediv__(self, other: int) -> 'Result':
        if self.value is None:
            return Result()
        elif isinstance(self.value, int) or isinstance(self.value, float):
            return Result(self.value / other)
        elif isinstance(self.value, tuple):
            solved = self.value[0]
            attempted = self.value[1]
            time = self.value[2] / other
            return Result((solved, attempted, time))
        else:
            return Result(self.value / other)

    def __lt__(self, other: 'Result') -> bool:
        if self.value is None or other.value is None:
            return True
        return float(self) < float(other)

    def __le__(self, other: 'Result') -> bool:
        if self.value is None or other.value is None:
            return True
        return float(self) <= float(other)

    def __eq__(self, other) -> bool:
        if self.value is None and other.value is None:
            return True
        return float(self) == float(other)

    def __ne__(self, other) -> bool:
        if self.value is None and other.value is None:
            return False
        return float(self) != float(other)

    def __gt__(self, other: 'Result') -> bool:
        if self.value is None or other.value is None:
            return True
        return float(self) > float(other)

    def __ge__(self, other: 'Result') -> bool:
        if self.value is None or other.value is None:
            return True
        return float(self) >= float(other)

    def __repr__(self) -> str:
        if self.value is None:
            return "No result"
        elif isinstance(self.value, int) or isinstance(self.value, float):
            return f"{self.value} moves"
        elif isinstance(self.value, tuple):
            time = _time_to_str(self.value[2])
            return f"{self.value[0]}/{self.value[1]} in {time}"
        else:
            return _time_to_str(self.value)


class Solve:
    def __init__(self, start: datetime, result: Result, category: str, source: str) -> None:
        self.start: datetime = start

        self.result: Result = result
        self.category: str = category.strip()
        self.source: str = source.strip()

    def __repr__(self) -> str:
        return f"{self.category}: {self.result} . {self.start.strftime('%c')} ({self.source})"

    def as_list(self) -> List[Union[datetime, Result, str]]:
        return [self.start, self.result, self.category, self.source]

    def as_dict(self) -> Dict[str, Union[datetime, Result, timedelta, str]]:
        return {
            "start": self.start,
            "result": self.result,
            "category": self.category,
            "source": self.source
        }


class SolveCollection(list):

    def as_dataframe(self) -> DataFrame:
        return DataFrame([solve.as_dict() for solve in self])

    def as_timeseries(self) -> Series:
        return Series({solve.start: solve.result for solve in self})
