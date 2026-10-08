from fractions import Fraction
import unittest

from boxes import Box, Interval, map_is_contained, polynomial_corner_range
from exact import Q5
from polynomial import Polynomial
from tree import (
    SubdivisionLeaf,
    SubdivisionNode,
    TreeValidationError,
    validate_subdivision_tree,
)


def unit_square() -> Box:
    return Box([Interval(0, 1), Interval(0, 1)])


class BoxTests(unittest.TestCase):
    def test_exact_interval_product_all_signs(self):
        product_interval = Interval(-2, 3).product(Interval(-5, 7))
        self.assertEqual(product_interval, Interval(-15, 21))

    def test_multiaffine_corner_minimisation(self):
        x = Polynomial.variable(2, 0)
        y = Polynomial.variable(2, 1)
        polynomial = 2 - 3 * x + y + 4 * x * y
        result = polynomial_corner_range(polynomial, unit_square())
        corner_values = [
            polynomial.evaluate(corner)
            for corner in unit_square().corners()
        ]
        self.assertEqual(result.lower, min(corner_values))
        self.assertEqual(result.upper, max(corner_values))

    def test_corner_rule_rejects_non_multiaffine_polynomial(self):
        x = Polynomial.variable(2, 0)
        with self.assertRaises(ValueError):
            polynomial_corner_range(x * x, unit_square())

    def test_exact_map_containment(self):
        x = Polynomial.variable(2, 0)
        y = Polynomial.variable(2, 1)
        coordinates = [x * y, x + y - x * y]
        self.assertTrue(
            map_is_contained(
                coordinates,
                unit_square(),
                Box([Interval(0, 1), Interval(0, 1)]),
            )
        )
        self.assertFalse(
            map_is_contained(
                coordinates,
                unit_square(),
                Box([Interval(0, Fraction(3, 4)), Interval(0, 1)]),
            )
        )

    def test_exact_box_containment(self):
        outer = Box([Interval(-1, 2), Interval(0, 5)])
        inner = Box([Interval(0, 1), Interval(2, 3)])
        enlarged = Box([Interval(-2, 1), Interval(2, 3)])
        self.assertTrue(outer.contains_box(inner))
        self.assertFalse(outer.contains_box(enlarged))


class TreeTests(unittest.TestCase):
    def make_valid_tree(self):
        root = unit_square()
        lower, upper = root.split(0)
        lower_lower, lower_upper = lower.split(1)
        tree = SubdivisionNode(
            0,
            root,
            SubdivisionNode(
                1,
                lower,
                SubdivisionLeaf("a", lower_lower),
                SubdivisionLeaf("b", lower_upper),
            ),
            SubdivisionLeaf("c", upper),
        )
        return root, tree

    def test_complete_tree(self):
        root, tree = self.make_valid_tree()
        leaves = validate_subdivision_tree(tree, root)
        self.assertEqual([leaf.identifier for leaf in leaves], ["a", "b", "c"])

    def test_missing_leaf(self):
        root, tree = self.make_valid_tree()
        broken = SubdivisionNode(tree.axis, tree.box, tree.lower, None)
        with self.assertRaisesRegex(TreeValidationError, "missing child"):
            validate_subdivision_tree(broken, root)

    def test_duplicate_leaf_identifier(self):
        root = unit_square()
        lower, upper = root.split(0)
        tree = SubdivisionNode(
            0,
            root,
            SubdivisionLeaf("same", lower),
            SubdivisionLeaf("same", upper),
        )
        with self.assertRaisesRegex(TreeValidationError, "duplicate"):
            validate_subdivision_tree(tree, root)

    def test_overlapping_or_malformed_child_pair(self):
        root = unit_square()
        lower, _ = root.split(0)
        tree = SubdivisionNode(
            0,
            root,
            SubdivisionLeaf("a", lower),
            SubdivisionLeaf("b", lower),
        )
        with self.assertRaisesRegex(TreeValidationError, "midpoint path"):
            validate_subdivision_tree(tree, root)

    def test_enlarged_leaf(self):
        root = unit_square()
        lower, upper = root.split(0)
        enlarged = Box([Interval(0, Fraction(3, 4)), Interval(0, 1)])
        tree = SubdivisionNode(
            0,
            root,
            SubdivisionLeaf("a", enlarged),
            SubdivisionLeaf("b", upper),
        )
        with self.assertRaisesRegex(TreeValidationError, "midpoint path"):
            validate_subdivision_tree(tree, root)

    def test_invalid_axis(self):
        root = unit_square()
        tree = SubdivisionNode(
            2,
            root,
            SubdivisionLeaf("a", root),
            SubdivisionLeaf("b", root),
        )
        with self.assertRaisesRegex(TreeValidationError, "axis"):
            validate_subdivision_tree(tree, root)


if __name__ == "__main__":
    unittest.main()
