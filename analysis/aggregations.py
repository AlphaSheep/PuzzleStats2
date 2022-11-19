import math
from bisect import insort, bisect_left
from collections import deque
from datetime import timedelta
from typing import TypeVar, Deque, Optional, List

T = TypeVar('T')


class MovingMean:
    def __init__(self, size: int):
        assert size > 0

        self.size: int = size
        self.values: Deque[T] = deque()
        self.sum: Optional[T] = None

    def __add__(self, new: T):
        self.values.append(new)
        if self.sum is None:
            self.sum = new
        else:
            self.sum += new

        if len(self.values) > self.size:
            self.sum -= self.values.popleft()
            return self
        elif len(self.values) == self.size:
            return self
        else:
            return self

    def get_mean(self) -> T:
        if len(self.values) == self.size:
            return self.sum / self.size
        else:
            return None


class MovingAverage:
    """An average is the mean of the middle, excluding the top and bottom 5% (rounded up)"""

    def __init__(self, size: int):
        assert size > 0
        self.size: int = size

        # Maintain two lists:
        #    values: a queue, in the order that elements are added
        #    sortedValues: a sorted list
        self.values: Deque[T] = deque()
        self.sortedValues: List[T] = []

        self.sum: Optional[T] = None

        self.cutoffSize: int = math.ceil(size / 20)  # Ignore top and bottom 5%

    def __add__(self, new: T):
        self.values.append(new)
        insort(self.sortedValues, new)

        # Add to the sum
        if self.sum is None:
            self.sum = new
        else:
            self.sum += new

        # Manage list size
        if len(self.values) > self.size:
            # List too big, need to get rid of oldest

            old = self.values.popleft()
            pos = bisect_left(self.sortedValues, old)
            del self.sortedValues[pos]

            self.sum -= old
        return self

    def get_average(self) -> Optional[T]:
        if len(self.values) == self.size:
            lower = sumt(self.sortedValues[:self.cutoffSize])
            upper = sumt(self.sortedValues[-self.cutoffSize:])
            middle_sum = (self.sum - lower - upper)
            divisor = (self.size - (2 * self.cutoffSize))
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
