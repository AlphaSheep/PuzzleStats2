import math
from abc import ABC
from bisect import insort, bisect_left
from collections import deque
from datetime import timedelta
from typing import TypeVar, Deque, Optional, List

T = TypeVar('T')


class BaseMovingWindow(ABC):
    def __init__(self, size: int):
        assert size > 0

        self._size: int = size
        self._values: Deque[T] = deque()
        self._sum: Optional[T] = None


class MovingMeanWindow(BaseMovingWindow):
    """
    Efficiently manages a moving window for getting the mean of the last N observations.
    """

    def __add__(self, new: T):
        self._values.append(new)
        if self._sum is None:
            self._sum = new
        else:
            self._sum += new

        if len(self._values) > self._size:
            self._sum -= self._values.popleft()
            return self
        elif len(self._values) == self._size:
            return self
        else:
            return self

    @property
    def value(self) -> Optional[T]:
        if len(self._values) == self._size:
            return self._sum / self._size
        else:
            return None


class MovingAverageWindow(BaseMovingWindow):
    """
    Efficiently manages a moving mean window for getting the average of the last N observations.
    An average is the mean of the middle, excluding the top and bottom 5% (rounded up).
    """

    def __init__(self, size: int):
        if size < 3:
            raise ValueError("Size must be at least 3 to calculate an average")

        super().__init__(size)

        self._sortedValues: List[T] = []
        self._cutoffSize: int = math.ceil(size / 20)  # Ignore top and bottom 5%

    def __add__(self, new: T):
        self._values.append(new)
        insort(self._sortedValues, new)

        # Add to the sum
        if self._sum is None:
            self._sum = new
        else:
            self._sum += new

        # Manage list size
        if len(self._values) > self._size:
            # List too big, need to get rid of oldest
            old = self._values.popleft()
            pos = bisect_left(self._sortedValues, old)
            del self._sortedValues[pos]
            self._sum -= old

        return self

    @property
    def value(self) -> Optional[T]:
        if len(self._values) == self._size:
            lower = sumt(self._sortedValues[:self._cutoffSize])
            upper = sumt(self._sortedValues[-self._cutoffSize:])
            middle_sum = (self._sum - lower - upper)
            divisor = (self._size - (2 * self._cutoffSize))
            return middle_sum / divisor
        else:
            return None


def sumt(times: List[T]) -> T:
    # Special sum that can also handle timeDeltas
    if len(times) > 0 and type(times[0]) is timedelta:
        total = timedelta(seconds=0)
        for t in times:
            total += t
    else:
        total = sum(times)
    return total


def average_excl_max_and_min(times: List[T]) -> T:
    return (sumt(times) - max(times) - min(times)) / (len(times) - 2)
