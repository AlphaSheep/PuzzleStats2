import unittest

from datetime import datetime, timedelta
from math import isnan

from solves import Statistic, StatisticCollection, Result


EXAMPLE_DATETIME = datetime(2000, 3, 2, 9, 8, 7)
EXAMPLE_RESULT = Result(timedelta(seconds=4.56))
EXAMPLE_CATEGORY = "Test Category"
EXAMPLE_SOURCE = "Unit tests"

ANOTHER_EXAMPLE_DATETIME = datetime(2001, 4, 5, 6, 7, 8)
ANOTHER_EXAMPLE_RESULT = Result(timedelta(seconds=1.23))
ANOTHER_EXAMPLE_CATEGORY = "Another Test Category"
ANOTHER_EXAMPLE_SOURCE = "More unit tests"


class TestResult(unittest.TestCase):

    def test_time_result_to_float(self):
        result = Result(timedelta(seconds=4.56))
        result_as_float = float(result)

        expected = 4.56
        self.assertEqual(result_as_float, expected)

    def test_number_result_to_float(self):
        result = Result(42)
        result_as_float = float(result)

        expected = 42
        self.assertEqual(result_as_float, expected)

    def test_multi_result_to_float(self):
        result = Result((3, 4, timedelta(seconds=567)))
        result_as_float = float(result)

        expected = 95056701
        self.assertEqual(result_as_float, expected)

    def test_null_result_to_float(self):
        result = Result(None)
        result_as_float = float(result)

        self.assertTrue(isnan(result_as_float))

    def test_add_numeric_result(self):
        result = Result(42) + Result(1)
        expected = Result(43)
        self.assertEqual(result, expected)

    def test_add_time_result(self):
        result = Result(timedelta(seconds=4.56)) + Result(timedelta(seconds=1.23))
        expected = Result(timedelta(seconds=5.79))
        self.assertEqual(result, expected)

    def test_add_multi_result(self):
        result = Result((3, 4, timedelta(seconds=567))) + Result((1, 2, timedelta(seconds=345)))
        expected = Result((4, 6, timedelta(seconds=912)))
        self.assertEqual(result, expected)

    def test_add_result_to_null_result(self):
        result = Result(None) + Result(5)
        expected = Result(5)
        self.assertEqual(result, expected)

    def test_sub_numeric_result(self):
        result = Result(42) - Result(1)
        expected = Result(41)
        self.assertEqual(result, expected)

    def test_sub_time_result(self):
        result = Result(timedelta(seconds=4.56)) - Result(timedelta(seconds=1.23))
        expected = Result(timedelta(seconds=3.33))
        self.assertEqual(result, expected)

    def test_sub_multi_result(self):
        result = Result((3, 4, timedelta(seconds=567))) - Result((1, 2, timedelta(seconds=345)))
        expected = Result((2, 2, timedelta(seconds=222)))
        self.assertEqual(result, expected)

    def test_sub_null_result(self):
        result = Result(5) - Result(None)
        expected = Result(5)
        self.assertEqual(result, expected)

    def test_sub_from_null_result_errors(self):
        with self.assertRaises(ValueError):
            expected = Result(None) - Result(5)
            if (expected):
                self.fail()

    def test_div_numeric_result(self):
        result = Result(42) / 2
        expected = Result(21)
        self.assertEqual(result, expected)

    def test_div_time_result(self):
        result = Result(timedelta(seconds=4.68)) / 2
        expected = Result(timedelta(seconds=2.34))
        self.assertEqual(result, expected)

    def test_div_null_result(self):
        result = Result(None) / 2
        expected = Result(None)
        self.assertEqual(result, expected)

    def test_compare_result(self):
        self.assertTrue(Result(1) < Result(2))
        self.assertFalse(Result(2) < Result(1))
        self.assertFalse(Result(1) < Result(1))

        self.assertTrue(Result(1) <= Result(2))
        self.assertFalse(Result(2) <= Result(1))
        self.assertTrue(Result(1) <= Result(1))

        self.assertFalse(Result(1) > Result(2))
        self.assertTrue(Result(2) > Result(1))
        self.assertFalse(Result(1) > Result(1))

        self.assertFalse(Result(1) >= Result(2))
        self.assertTrue(Result(2) >= Result(1))
        self.assertTrue(Result(1) >= Result(1))

        self.assertFalse(Result(1) == Result(2))
        self.assertFalse(Result(2) == Result(1))
        self.assertTrue(Result(1) == Result(1))

        self.assertTrue(Result(1) != Result(2))
        self.assertTrue(Result(2) != Result(1))
        self.assertFalse(Result(1) != Result(1))

    def test_compare_null_result(self):
        self.assertTrue(Result(None) < Result(2))
        self.assertTrue(Result(2) < Result(None))
        self.assertTrue(Result(None) < Result(None))

        self.assertTrue(Result(None) <= Result(2))
        self.assertTrue(Result(2) <= Result(None))
        self.assertTrue(Result(None) <= Result(None))

        self.assertTrue(Result(None) > Result(2))
        self.assertTrue(Result(2) > Result(None))
        self.assertTrue(Result(None) > Result(None))

        self.assertTrue(Result(None) >= Result(2))
        self.assertTrue(Result(2) >= Result(None))
        self.assertTrue(Result(None) >= Result(None))

        self.assertFalse(Result(None) == Result(2))
        self.assertFalse(Result(2) == Result(None))
        self.assertTrue(Result(None) == Result(None))

        self.assertTrue(Result(None) != Result(2))
        self.assertTrue(Result(2) != Result(None))
        self.assertFalse(Result(None) != Result(None))


class TestStatistic(unittest.TestCase):

    def test_statistic_to_list(self):
        result = _get_a_statistic()
        result_as_list = result.as_list()

        expected = [EXAMPLE_DATETIME, EXAMPLE_RESULT, EXAMPLE_CATEGORY, EXAMPLE_SOURCE]
        self.assertEqual(result_as_list, expected)

    def test_statistic_to_dict(self):
        result = _get_a_statistic()
        result_as_dict = result.as_dict()

        expected = {
            "date": EXAMPLE_DATETIME,
            "result": EXAMPLE_RESULT,
            "category": EXAMPLE_CATEGORY,
            "source": EXAMPLE_SOURCE
        }
        self.assertEqual(result_as_dict, expected)


class TestStatisticCollection(unittest.TestCase):

    def assertStatisticEqual(self, actual: Statistic, expected: Statistic):
        self.assertEqual(actual.date, expected.date)
        self.assertAlmostEqual(float(actual.result), float(expected.result))
        self.assertEqual(actual.category, expected.category)
        self.assertEqual(actual.source, expected.source)

    def test_append_statistic(self):
        collection = StatisticCollection()

        self.assertEqual(len(collection), 0)

        collection.append(_get_a_statistic())

        self.assertEqual(len(collection), 1)

        expected = [_get_a_statistic()]
        self.assertStatisticEqual(collection[0], expected[0])

    def test_add_statistic_collection(self):
        collection = StatisticCollection([_get_a_statistic()])

        self.assertEqual(len(collection), 1)

        collection += StatisticCollection([_get_another_statistic()])

        self.assertEqual(len(collection), 2)

        expected = [_get_a_statistic(), _get_another_statistic()]
        self.assertStatisticEqual(collection[0], expected[0])
        self.assertStatisticEqual(collection[1], expected[1])

    def test_iter_statistic_collection(self):
        collection = StatisticCollection([_get_a_statistic(), _get_another_statistic()])

        self.assertEqual(len(collection), 2)

        expected = [_get_a_statistic(), _get_another_statistic()]
        for actual, expected in zip(collection, expected):
            self.assertStatisticEqual(actual, expected)

    def test_get_statistic_collection_properties(self):
        collection = StatisticCollection([_get_a_statistic(), _get_another_statistic()])
        self.assertEqual(collection.category, [EXAMPLE_CATEGORY, ANOTHER_EXAMPLE_CATEGORY])
        self.assertEqual(collection.source, [EXAMPLE_SOURCE, ANOTHER_EXAMPLE_SOURCE])
        self.assertEqual(collection.date, [EXAMPLE_DATETIME, ANOTHER_EXAMPLE_DATETIME])
        self.assertAlmostEqual(float(collection.result[0]), float(EXAMPLE_RESULT))
        self.assertAlmostEqual(float(collection.result[1]), float(ANOTHER_EXAMPLE_RESULT))

    def test_filter_statistic_collection(self):
        collection = StatisticCollection([_get_a_statistic(), _get_another_statistic()])
        self.assertEqual(len(collection), 2)

        filtered = collection.filter([True, False])
        self.assertEqual(len(filtered), 1)

        expected = [_get_a_statistic()]
        self.assertStatisticEqual(filtered[0], expected[0])

    def test_sort_statistic_collection(self):
        collection = StatisticCollection([_get_another_statistic(), _get_a_statistic()])
        self.assertEqual(len(collection), 2)

        collection.sort()
        self.assertEqual(len(collection), 2)

        expected = [_get_a_statistic(), _get_another_statistic()]
        self.assertStatisticEqual(collection[0], expected[0])
        self.assertStatisticEqual(collection[1], expected[1])




def _get_a_statistic() -> Statistic:
    start = EXAMPLE_DATETIME
    time = EXAMPLE_RESULT
    category = EXAMPLE_CATEGORY
    source = EXAMPLE_SOURCE
    return Statistic(start, time, category, source)


def _get_another_statistic() -> Statistic:
    start = ANOTHER_EXAMPLE_DATETIME
    time = ANOTHER_EXAMPLE_RESULT
    category = ANOTHER_EXAMPLE_CATEGORY
    source = ANOTHER_EXAMPLE_SOURCE
    return Statistic(start, time, category, source)


if __name__ == '__main__':
    unittest.main()
