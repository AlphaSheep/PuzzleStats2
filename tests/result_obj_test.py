import unittest
from datetime import datetime, timedelta

from solves import Solve, Result


EXAMPLE_DATETIME = datetime(2000, 3, 2, 9, 8, 7)
EXAMPLE_RESULT = Result(timedelta(seconds=4.56))
EXAMPLE_CATEGORY = "Test Category"
EXAMPLE_PENALTY = timedelta(seconds=0)
EXAMPLE_SOURCE = "Unit tests"


class TestResult(unittest.TestCase):
    def test_result_to_list(self):
        result = _get_a_result()
        result_as_list = result.as_list()

        expected = [EXAMPLE_DATETIME, EXAMPLE_RESULT, EXAMPLE_CATEGORY, EXAMPLE_SOURCE]
        self.assertEqual(result_as_list, expected)


def _get_a_result() -> Solve:
    start = EXAMPLE_DATETIME
    time = EXAMPLE_RESULT
    category = EXAMPLE_CATEGORY
    penalty = EXAMPLE_PENALTY
    source = EXAMPLE_SOURCE
    return Solve(start, time, category, source)


if __name__ == '__main__':
    unittest.main()
