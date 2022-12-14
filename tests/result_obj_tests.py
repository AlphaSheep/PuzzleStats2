import unittest
from datetime import datetime, timedelta

from result import Result


EXAMPLE_DATETIME = datetime(2000, 3, 2, 9, 8, 7)
EXAMPLE_TIMEDELTA = timedelta(seconds=4.56)
EXAMPLE_CATEGORY = "Test Category"
EXAMPLE_PENALTY = timedelta(seconds=0)
EXAMPLE_SOURCE = "Unit tests"


class TestResult(unittest.TestCase):
    def test_result_to_list(self):
        result = _get_a_result()
        result_as_list = result.as_list()

        expected = [EXAMPLE_DATETIME, EXAMPLE_TIMEDELTA, EXAMPLE_CATEGORY, EXAMPLE_PENALTY, EXAMPLE_SOURCE]
        self.assertEqual(result_as_list, expected)


def _get_a_result() -> Result:
    start = EXAMPLE_DATETIME
    time = EXAMPLE_TIMEDELTA
    category = EXAMPLE_CATEGORY
    penalty = EXAMPLE_PENALTY
    source = EXAMPLE_SOURCE
    return Result(start, time, category, penalty, source)

if __name__ == '__main__':
    unittest.main()
