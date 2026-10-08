from fractions import Fraction
from itertools import product
import unittest

from bernstein import all_strictly_positive, bernstein_coefficients, evaluate_bernstein
from exact import Q5
from polynomial import Polynomial


class BernsteinTests(unittest.TestCase):
    def test_constant(self):
        polynomial = Polynomial.constant(2, Q5.rational(Fraction(7, 3)))
        coefficients = bernstein_coefficients(
            polynomial,
            [(Fraction(-2), Fraction(5)), (Fraction(3), Fraction(9))],
        )
        self.assertEqual(coefficients, {(0, 0): Q5.rational(Fraction(7, 3))})

    def test_univariate_linear_on_nonunit_box(self):
        x = Polynomial.variable(1, 0)
        coefficients = bernstein_coefficients(x, [(Fraction(2), Fraction(4))])
        self.assertEqual(coefficients[(0,)], Q5.rational(2))
        self.assertEqual(coefficients[(1,)], Q5.rational(4))

    def test_univariate_quadratic_on_nonunit_box(self):
        x = Polynomial.variable(1, 0)
        coefficients = bernstein_coefficients(x * x, [(Fraction(1), Fraction(3))])
        self.assertEqual(
            [coefficients[(index,)] for index in range(3)],
            [Q5.rational(1), Q5.rational(3), Q5.rational(9)],
        )

    def test_article_quadratic_and_subdivision(self):
        x = Polynomial.variable(1, 0)
        polynomial = -1 + 3 * x - 3 * x * x
        whole = bernstein_coefficients(polynomial, [(Fraction(0), Fraction(1))])
        self.assertEqual(
            [whole[(index,)] for index in range(3)],
            [Q5.rational(-1), Q5.rational(Fraction(1, 2)), Q5.rational(-1)],
        )
        left = bernstein_coefficients(polynomial, [(Fraction(0), Fraction(1, 2))])
        right = bernstein_coefficients(polynomial, [(Fraction(1, 2), Fraction(1))])
        self.assertTrue(all(value.sign() < 0 for value in left.values()))
        self.assertTrue(all(value.sign() < 0 for value in right.values()))

    def test_multivariate_tensor_product(self):
        x = Polynomial.variable(2, 0)
        y = Polynomial.variable(2, 1)
        polynomial = (1 + x) * (2 - y)
        coefficients = bernstein_coefficients(
            polynomial,
            [(Fraction(0), Fraction(1)), (Fraction(0), Fraction(1))],
        )
        expected = {
            (0, 0): Q5.rational(2),
            (0, 1): Q5.rational(1),
            (1, 0): Q5.rational(4),
            (1, 1): Q5.rational(2),
        }
        self.assertEqual(coefficients, expected)
        self.assertTrue(all_strictly_positive(coefficients))

    def test_deliberately_nonpositive_coefficient(self):
        x = Polynomial.variable(1, 0)
        polynomial = x * x
        coefficients = bernstein_coefficients(polynomial, [(Fraction(-1), Fraction(1))])
        self.assertEqual(
            [coefficients[(index,)] for index in range(3)],
            [Q5.rational(1), Q5.rational(-1), Q5.rational(1)],
        )
        self.assertFalse(all_strictly_positive(coefficients))

    def test_zero_coefficient_fails_strict_sign(self):
        x = Polynomial.variable(1, 0)
        coefficients = bernstein_coefficients(x, [(Fraction(0), Fraction(1))])
        self.assertEqual(coefficients[(0,)].sign(), 0)
        self.assertFalse(all_strictly_positive(coefficients))

    def test_round_trip_at_rational_points(self):
        x = Polynomial.variable(2, 0)
        y = Polynomial.variable(2, 1)
        polynomial = Q5(Fraction(2), Fraction(-1)) * x * x + x * y + 3 * y + 5
        box = [(Fraction(-2), Fraction(3)), (Fraction(1, 3), Fraction(7, 3))]
        degrees = polynomial.degrees()
        coefficients = bernstein_coefficients(polynomial, box)
        for unit_point in (
            (Fraction(0), Fraction(0)),
            (Fraction(1), Fraction(1)),
            (Fraction(2, 5), Fraction(3, 7)),
        ):
            actual_point = [
                Q5.rational(lower + (upper - lower) * coordinate)
                for (lower, upper), coordinate in zip(box, unit_point)
            ]
            self.assertEqual(
                evaluate_bernstein(coefficients, degrees, unit_point),
                polynomial.evaluate(actual_point),
            )


if __name__ == "__main__":
    unittest.main()
