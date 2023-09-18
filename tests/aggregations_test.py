import unittest

from analysis.aggregations import MovingMeanWindow, MovingAverageWindow
from solves import Result


class TestMovingWindows(unittest.TestCase):
    def test_moving_mean_empty_before_size_reached(self):
        window = MovingMeanWindow(3)
        self.assertIsNone(window.value)
        window += Result(1)
        self.assertIsNone(window.value)
        window += Result(2)
        self.assertIsNone(window.value)
        window += Result(3)
        self.assertIsNotNone(window.value)

    def test_moving_average_empty_before_size_reached(self):
        window = MovingAverageWindow(3)
        self.assertIsNone(window.value)
        window += Result(1)
        self.assertIsNone(window.value)
        window += Result(2)
        self.assertIsNone(window.value)
        window += Result(3)
        self.assertIsNotNone(window.value)

    def test_average_errors_if_size_less_than_3(self):
        try:
            window = MovingAverageWindow(2)
        except ValueError:
            pass
        else:
            self.fail()

    def test_moving_mean_value(self):
        window = MovingMeanWindow(4)
        window += Result(200.2)
        window += Result(1000.1)
        window += Result(4.4)
        window += Result(30.3)
        if window.value is not None:
            self.assertAlmostEqual(float(window.value), 308.75)
        else:
            self.fail()

        window += Result(50000.1)
        if window.value is not None:
            self.assertAlmostEqual(float(window.value), 12758.725)
        else:
            self.fail()

    def test_moving_average_value(self):
        window = MovingAverageWindow(4)
        window += Result(200.2)
        window += Result(1000.1)
        window += Result(4.4)
        window += Result(30.3)
        if window.value is not None:
            self.assertAlmostEqual(float(window.value), 115.25)
        else:
            self.fail()

        window += Result(50000.1)
        if window.value is not None:
            self.assertAlmostEqual(float(window.value), 515.2)
        else:
            self.fail()


if __name__ == '__main__':
    unittest.main()
