from fractions import Fraction
import unittest

from exact import Q5
from polynomial import MonomialDivisionError, Polynomial, monomial


class PolynomialTests(unittest.TestCase):
    def test_addition_and_multiplication(self):
        x = Polynomial.variable(2, 0)
        y = Polynomial.variable(2, 1)
        polynomial = (x + 2 * y) * (x - y)
        self.assertEqual(polynomial.coefficient((2, 0)), Q5.rational(1))
        self.assertEqual(polynomial.coefficient((1, 1)), Q5.rational(1))
        self.assertEqual(polynomial.coefficient((0, 2)), Q5.rational(-2))
        self.assertEqual(polynomial.evaluate([3, 4]), Q5.rational(-11))

    def test_affine_substitution(self):
        x = Polynomial.variable(2, 0)
        y = Polynomial.variable(2, 1)
        polynomial = x * x + y
        pulled_back = polynomial.affine_substitute(
            [Q5.rational(1), Q5.rational(-1)],
            [
                [Q5.rational(2), Q5.rational(0)],
                [Q5.rational(1), Q5.rational(3)],
            ],
        )
        point = [Q5.rational(Fraction(1, 2)), Q5.rational(Fraction(2, 3))]
        source = [
            Q5.rational(1) + 2 * point[0],
            Q5.rational(-1) + point[0] + 3 * point[1],
        ]
        self.assertEqual(pulled_back.evaluate(point), polynomial.evaluate(source))

    def test_multiaffine_substitution(self):
        x = Polynomial.variable(2, 0)
        y = Polynomial.variable(2, 1)
        source = x * x + y
        a = Polynomial.variable(3, 0)
        b = Polynomial.variable(3, 1)
        c = Polynomial.variable(3, 2)
        pulled_back = source.substitute([a * b + 1, b + c])
        point = [Q5.rational(2), Q5.rational(3), Q5.rational(5)]
        self.assertEqual(
            pulled_back.evaluate(point),
            source.evaluate([point[0] * point[1] + 1, point[1] + point[2]]),
        )

    def test_exact_monomial_division(self):
        polynomial = Polynomial(
            3,
            {
                (2, 1, 0): Q5.rational(3),
                (1, 3, 2): Q5(Fraction(1), Fraction(1)),
            },
        )
        quotient = polynomial.divide_monomial((1, 1, 0))
        self.assertEqual(quotient.multiply_monomial((1, 1, 0)), polynomial)

    def test_failed_monomial_division(self):
        polynomial = monomial(2, (1, 0)) + monomial(2, (0, 1))
        self.assertFalse(polynomial.divisible_by_monomial((1, 0)))
        with self.assertRaises(MonomialDivisionError):
            polynomial.divide_monomial((1, 0))

    def test_cancellation_removes_zero_terms(self):
        x = Polynomial.variable(1, 0)
        self.assertTrue((x - x).is_zero())


if __name__ == "__main__":
    unittest.main()
