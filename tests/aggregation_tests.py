import unittest

from analysis.aggregations import MovingMeanWindow, MovingAverageWindow


class TestMovingWindows(unittest.TestCase):
    def test_moving_mean_empty_before_size_reached(self):
        window = MovingMeanWindow(3)
        self.assertIsNone(window.value)
        window += 1
        self.assertIsNone(window.value)
        window += 2
        self.assertIsNone(window.value)
        window += 3
        self.assertIsNotNone(window.value)

    def test_moving_average_empty_before_size_reached(self):
        window = MovingAverageWindow(3)
        self.assertIsNone(window.value)
        window += 1
        self.assertIsNone(window.value)
        window += 2
        self.assertIsNone(window.value)
        window += 3
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
        window += 200.2
        window += 1000.1
        window += 4.4
        window += 30.3
        self.assertAlmostEqual(window.value, 308.75)

        window += 50000.1
        self.assertAlmostEqual(window.value, 12758.725)

    def test_moving_average_value(self):
        window = MovingAverageWindow(4)
        window += 200.2
        window += 1000.1
        window += 4.4
        window += 30.3
        self.assertAlmostEqual(window.value, 115.25)

        window += 50000.1
        self.assertAlmostEqual(window.value, 515.2)


if __name__ == '__main__':
    unittest.main()
