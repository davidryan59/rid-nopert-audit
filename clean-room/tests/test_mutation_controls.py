from fractions import Fraction
import unittest

from bernstein import all_strictly_positive, bernstein_coefficients
from boxes import Box, Interval, polynomial_corner_range
from exact import Q5
from polynomial import MonomialDivisionError, Polynomial


UNIT_BOX_2 = [(Fraction(0), Fraction(1)), (Fraction(0), Fraction(1))]


class MathematicalMutationControls(unittest.TestCase):
    def setUp(self):
        self.x = Polynomial.variable(2, 0)
        self.y = Polynomial.variable(2, 1)
        # The intended divided quotient is 1 + x, strictly positive.
        self.pulled_witness = self.x * self.y * (1 + self.x)

    def test_correct_distance_factor_positive_control(self):
        quotient = self.pulled_witness.divide_monomial((1, 1))
        coefficients = bernstein_coefficients(quotient, UNIT_BOX_2)
        self.assertTrue(all_strictly_positive(coefficients))

    def test_wrong_distance_factor_is_rejected(self):
        with self.assertRaises(MonomialDivisionError):
            self.pulled_witness.divide_monomial((2, 1))

    def test_incorrect_exponent_is_rejected(self):
        with self.assertRaises(MonomialDivisionError):
            self.pulled_witness.divide_monomial((1, 2))

    def test_omitted_factor_fails_strict_positivity(self):
        quotient = self.pulled_witness.divide_monomial((1, 0))
        coefficients = bernstein_coefficients(quotient, UNIT_BOX_2)
        self.assertFalse(all_strictly_positive(coefficients))
        self.assertTrue(any(coefficient.sign() == 0 for coefficient in coefficients.values()))

    def test_perturbed_witness_coefficient_is_detected(self):
        mutated = self.x * self.y * (self.x - Fraction(1, 2))
        quotient = mutated.divide_monomial((1, 1))
        coefficients = bernstein_coefficients(quotient, UNIT_BOX_2)
        self.assertFalse(all_strictly_positive(coefficients))
        self.assertTrue(any(coefficient.sign() < 0 for coefficient in coefficients.values()))

    def test_failed_exact_division_is_detected(self):
        mutated = self.pulled_witness + self.y
        with self.assertRaises(MonomialDivisionError):
            mutated.divide_monomial((1, 1))

    def test_invalid_support_corner_is_detected(self):
        support = self.x + self.y - Fraction(3, 2)
        support_range = polynomial_corner_range(
            support,
            Box([Interval(0, 1), Interval(0, 1)]),
        )
        # Support conditions require support <= 0 throughout the cell.
        self.assertGreater(support_range.upper, Q5.rational(0))

    def test_valid_support_corners_positive_control(self):
        support = self.x + self.y - 2
        support_range = polynomial_corner_range(
            support,
            Box([Interval(0, 1), Interval(0, 1)]),
        )
        self.assertLessEqual(support_range.upper, Q5.rational(0))

    def test_zero_bernstein_coefficient_is_detected(self):
        quotient = self.x
        coefficients = bernstein_coefficients(quotient, UNIT_BOX_2)
        self.assertFalse(all_strictly_positive(coefficients))
        self.assertTrue(any(coefficient.sign() == 0 for coefficient in coefficients.values()))

    def test_negative_bernstein_coefficient_is_detected(self):
        quotient = self.x - Fraction(1, 2)
        coefficients = bernstein_coefficients(quotient, UNIT_BOX_2)
        self.assertFalse(all_strictly_positive(coefficients))
        self.assertTrue(any(coefficient.sign() < 0 for coefficient in coefficients.values()))


if __name__ == "__main__":
    unittest.main()
