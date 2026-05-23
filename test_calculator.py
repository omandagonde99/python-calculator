"""
Unit Tests for Python Calculator SafeMathEvaluator
"""

import unittest
import math
from calculator import SafeMathEvaluator

class MockController:
    """Mock controller to supply is_degrees property to SafeMathEvaluator."""
    def __init__(self):
        self.is_degrees = True


class TestSafeMathEvaluator(unittest.TestCase):
    def setUp(self):
        self.controller = MockController()
        self.evaluator = SafeMathEvaluator(self.controller)

    def test_basic_arithmetic(self):
        self.assertEqual(self.evaluator.evaluate("2 + 3"), 5)
        self.assertEqual(self.evaluator.evaluate("10 - 4"), 6)
        self.assertEqual(self.evaluator.evaluate("3 × 4"), 12)
        self.assertEqual(self.evaluator.evaluate("10 ÷ 2"), 5)
        self.assertEqual(self.evaluator.evaluate("-5 + 3"), -2)

    def test_precedence_and_parentheses(self):
        self.assertEqual(self.evaluator.evaluate("2 + 3 × 4"), 14)
        self.assertEqual(self.evaluator.evaluate("(2 + 3) × 4"), 20)
        self.assertEqual(self.evaluator.evaluate("2 ^ 3 ^ 2"), 512)  # right-associative power

    def test_float_precision(self):
        self.assertEqual(self.evaluator.evaluate("0.1 + 0.2"), 0.3)
        self.assertAlmostEqual(self.evaluator.evaluate("1 ÷ 3"), 1/3, places=12)

    def test_modulo(self):
        self.assertEqual(self.evaluator.evaluate("10 % 3"), 1)

    def test_trigonometry_degrees(self):
        self.controller.is_degrees = True
        self.assertAlmostEqual(self.evaluator.evaluate("sin(30)"), 0.5)
        self.assertAlmostEqual(self.evaluator.evaluate("cos(60)"), 0.5)
        self.assertAlmostEqual(self.evaluator.evaluate("tan(45)"), 1.0)

    def test_trigonometry_radians(self):
        self.controller.is_degrees = False
        self.assertAlmostEqual(self.evaluator.evaluate("sin(pi ÷ 6)"), 0.5)
        self.assertAlmostEqual(self.evaluator.evaluate("cos(pi ÷ 3)"), 0.5)

    def test_logarithms(self):
        self.assertEqual(self.evaluator.evaluate("log(100)"), 2)
        self.assertAlmostEqual(self.evaluator.evaluate("ln(e)"), 1.0)

    def test_square_root_and_abs(self):
        self.assertEqual(self.evaluator.evaluate("sqrt(81)"), 9)
        self.assertEqual(self.evaluator.evaluate("abs(-42)"), 42)

    def test_factorial(self):
        self.assertEqual(self.evaluator.evaluate("fact(5)"), 120)
        self.assertEqual(self.evaluator.evaluate("fact(0)"), 1)

    def test_constants(self):
        self.assertAlmostEqual(self.evaluator.evaluate("pi"), math.pi, places=12)
        self.assertAlmostEqual(self.evaluator.evaluate("e"), math.e, places=12)

    def test_error_handling(self):
        with self.assertRaises(ZeroDivisionError):
            self.evaluator.evaluate("5 ÷ 0")
        with self.assertRaises(ValueError):
            self.evaluator.evaluate("invalid_expression")
        with self.assertRaises(ValueError):
            self.evaluator.evaluate("fact(-1)")


if __name__ == "__main__":
    unittest.main()
