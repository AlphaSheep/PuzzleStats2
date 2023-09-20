from typing import Deque, Optional, List

import math
from abc import ABC, abstractmethod
from bisect import insort, bisect_left
from collections import deque
from solves import Result


class BaseMovingWindow(ABC):
    def __init__(self, size: int):
        assert size > 0
        self._size: int = size
        self.reset()

    def reset(self) -> None:
        self._values: Deque[Result] = deque()
        self._sum: Result = Result(None)

    @abstractmethod
    def __add__(self, new: Result):
        raise NotImplementedError()

    @abstractmethod
    def get_current_result(self) -> Result:
        raise NotImplementedError()

    def calculate(self: 'BaseMovingWindow', y: List[Result]) -> List[Result]:
        self.reset()
        result: List[Result] = []
        for value in y:
            self += value
            result.append(self.get_current_result())
        return result


class MovingMeanWindow(BaseMovingWindow):
    """
    Efficiently manages a moving window for getting the mean of the last N observations.
    """

    def __add__(self, new: Result):
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

    def get_current_result(self) -> Result:
        if self._sum is not None and len(self._values) == self._size:
            return self._sum / self._size
        else:
            return Result(None)


class MovingAverageWindow(BaseMovingWindow):
    """
    Efficiently manages a moving window for getting the average of the last N observations.
    An average is the mean of the middle, excluding the top and bottom 5% (rounded up).
    """

    def __init__(self, size: int):
        if size < 3:
            raise ValueError("Size must be at least 3 to calculate an average")

        super().__init__(size)

        self._sortedValues: List[Result] = []
        self._cutoffSize: int = math.ceil(size / 20)  # Ignore top and bottom 5%

        self._lower_sum: Result = Result(None)
        self._upper_sum: Result = Result(None)

    def __add__(self, new: Result):

        is_big_enough = len(self._sortedValues) >= self._cutoffSize

        low_to_drop = self._sortedValues[self._cutoffSize - 1] if is_big_enough else Result()
        high_to_drop = self._sortedValues[-self._cutoffSize] if is_big_enough else Result()

        self._values.append(new)
        pos = bisect_left(self._sortedValues, new)
        self._sortedValues.insert(pos, new)

        # Add to the sum
        if self._sum is None:
            self._sum = new
        else:
            self._sum += new

        if pos < self._cutoffSize:
            self._lower_sum += new - low_to_drop
        if pos >= (len(self._values) - self._cutoffSize):
            self._upper_sum += new - high_to_drop

        # Manage list size
        if len(self._values) > self._size:
            # List too big, need to get rid of oldest
            old = self._values.popleft()
            pos = bisect_left(self._sortedValues, old)

            next_lowest = self._sortedValues[self._cutoffSize]
            next_highest = self._sortedValues[-self._cutoffSize - 1]

            # Handle if the value is in the cutoff range
            if pos < self._cutoffSize:
                self._lower_sum -= old
                self._lower_sum += next_lowest
            elif pos >= (len(self._values) - self._cutoffSize):
                self._upper_sum -= old
                self._upper_sum += next_highest

            # Drop the old value
            del self._sortedValues[pos]
            self._sum -= old

        return self


    def get_current_result(self) -> Result:
        if self._sum is not None and len(self._values) == self._size:
            middle_sum = (self._sum - self._lower_sum - self._upper_sum)
            divisor = (self._size - (2 * self._cutoffSize))
            return middle_sum / divisor
        else:
            return Result(None)

