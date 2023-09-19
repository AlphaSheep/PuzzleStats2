import unittest

from analysis.aggregations import MovingMeanWindow, MovingAverageWindow
from solves import Result


class TestMovingWindows(unittest.TestCase):
    def test_moving_mean_empty_before_size_reached(self):
        window = MovingMeanWindow(3)
        self.assertIsNone(window.get_current_result().value)
        window += Result(1)
        self.assertIsNone(window.get_current_result().value)
        window += Result(2)
        self.assertIsNone(window.get_current_result().value)
        window += Result(3)
        self.assertIsNotNone(window.get_current_result().value)

    def test_moving_average_empty_before_size_reached(self):
        window = MovingAverageWindow(3)
        self.assertIsNone(window.get_current_result().value)
        window += Result(1)
        self.assertIsNone(window.get_current_result().value)
        window += Result(2)
        self.assertIsNone(window.get_current_result().value)
        window += Result(3)
        self.assertIsNotNone(window.get_current_result().value)

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
        result = window.get_current_result()
        self.assertIsNotNone(result.value)
        self.assertAlmostEqual(float(result), 308.75)

        window += Result(50000.1)
        result = window.get_current_result()
        self.assertIsNotNone(result.value)
        self.assertAlmostEqual(float(result), 12758.725)

    def test_moving_average_value(self):
        window = MovingAverageWindow(4)
        window += Result(200.2)
        window += Result(1000.1)
        window += Result(4.4)
        window += Result(30.3)
        result = window.get_current_result()
        self.assertIsNotNone(result.value)
        self.assertAlmostEqual(float(result), 115.25)

        window += Result(50000.1)
        result = window.get_current_result()
        self.assertIsNotNone(result.value)
        self.assertAlmostEqual(float(result), 515.2)

    def test_calculate_average_from_list(self):
        input = [Result(i) for i in [
            15, 27, 6, 18, 12 ,1 ,24, 9, 3 ,21, 30 ,33 ,6 ,1 ,12 ,36 ,9, 18
        ]]
        expected = [Result(i) for i in [
            None, None, None, None, 15, 12, 12, 13, 8, 11, 18, 20, 19, 19, 16, 17, 9, 13
        ]]

        window = MovingAverageWindow(5)
        averages = window.calculate(input)

        self.assertEqual(len(averages), len(input))

        self.assertIsNone(averages[0].value)
        self.assertIsNone(averages[1].value)
        self.assertIsNone(averages[2].value)
        self.assertIsNone(averages[3].value)
        for i in range(4, len(input)):
            self.assertAlmostEqual(float(averages[i]), float(expected[i]))



if __name__ == '__main__':
    unittest.main()
