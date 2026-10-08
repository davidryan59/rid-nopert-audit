from fractions import Fraction
import unittest

from exact import Q5, SQRT5, parse_fraction


class Q5Tests(unittest.TestCase):
    def test_field_operations(self):
        x = Q5(Fraction(3, 2), Fraction(-2, 3))
        y = Q5(Fraction(-1, 4), Fraction(5, 7))
        self.assertEqual((x + y) - y, x)
        self.assertEqual((x * y) / y, x)
        self.assertEqual(x * x.reciprocal(), Q5.rational(1))

    def test_all_sign_shapes(self):
        cases = [
            (Q5(0, 0), 0),
            (Q5(3, 0), 1),
            (Q5(-3, 0), -1),
            (Q5(0, 4), 1),
            (Q5(0, -4), -1),
            (Q5(2, 3), 1),
            (Q5(-2, -3), -1),
            (Q5(3, -1), 1),
            (Q5(-3, 1), -1),
            (Q5(2, -1), -1),
            (Q5(-2, 1), 1),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(value.sign(), expected)

    def test_near_cancellation_is_exact(self):
        # 2.236067 < sqrt(5) < 2.236068, decided by rational squares.
        below = Q5(Fraction(-2_236_067, 1_000_000), Fraction(1))
        above = Q5(Fraction(-2_236_068, 1_000_000), Fraction(1))
        self.assertEqual(below.sign(), 1)
        self.assertEqual(above.sign(), -1)
        self.assertEqual((below - below).sign(), 0)

    def test_comparison(self):
        self.assertGreater(SQRT5, Q5.rational(2))
        self.assertLess(SQRT5, Q5.rational(Fraction(9, 4)))

    def test_json_round_trip(self):
        value = Q5(Fraction(-7, 11), Fraction(13, 17))
        self.assertEqual(Q5.from_json(value.to_json()), value)

    def test_rational_parser_rejects_noncanonical_grammar(self):
        self.assertEqual(parse_fraction("-6/8"), Fraction(-3, 4))
        for invalid in (True, 1.25, "0.5", " 1/2", "1//2", ""):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    parse_fraction(invalid)


if __name__ == "__main__":
    unittest.main()
