#!/usr/bin/env python3
"""Independent unit and mutation tests for the clean-room checker."""

import copy
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import checker


LOCAL_ZERO = checker.INPUT_DIR / "local" / "0.json"


class ExactArithmeticTests(unittest.TestCase):
    def test_rational_canonical_forms(self):
        self.assertEqual(checker.parse_rational("-7/3"), Fraction(-7, 3))
        for invalid in ("+1", "01", "-0", "2/1", "2/4", "1/-2"):
            with self.subTest(invalid=invalid), self.assertRaises(checker.CheckError):
                checker.parse_rational(invalid)

    def test_quadratic_field_sign(self):
        self.assertGreater(checker.K(Fraction(-2), Fraction(1)).sign(), 0)
        self.assertLess(checker.K(Fraction(2), Fraction(-1)).sign(), 0)
        self.assertGreater(checker.K(Fraction(5), Fraction(-2)).sign(), 0)
        self.assertEqual((checker.K(Fraction(1), Fraction(1)) /
                          checker.K(Fraction(1), Fraction(-1))),
                         checker.K(Fraction(-3, 2), Fraction(-1, 2)))

    def test_exact_monomial_division(self):
        polynomial = {(2, 1, 0, 0, 0): checker.K(Fraction(3))}
        self.assertEqual(checker.pdivide_monomial(polynomial, (1, 1, 0, 0, 0), "test"),
                         {(1, 0, 0, 0, 0): checker.K(Fraction(3))})
        with self.assertRaises(checker.CheckError):
            checker.pdivide_monomial(polynomial, (3, 0, 0, 0, 0), "test")

    def test_strict_bernstein_sign(self):
        cell = tuple((Fraction(0), Fraction(1)) for _ in range(5))
        self.assertEqual(checker.require_negative_bernstein(checker.pconst(-1), cell, "test"), 1)
        with self.assertRaises(checker.CheckError):
            checker.require_negative_bernstein(checker.pvar(0), cell, "test")


class GrammarAndSpecificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specification = checker.Specification()

    def test_specification_counts_and_generated_inventory(self):
        self.assertEqual(len(self.specification.vertices), 60)
        self.assertEqual(len(self.specification.inequality_rows), 73)
        self.assertEqual(len(self.specification.cover_by_path), 38)
        self.assertEqual(sum(len(cover["zooms"]) for cover in self.specification.inventory["covers"]), 334)

    def test_tree_preorder_and_closed_midpoint(self):
        root = tuple((Fraction(0), Fraction(1)) for _ in range(5))
        leaves = checker.parse_tree("0..", root, "test")
        self.assertEqual(leaves[0][0], (Fraction(0), Fraction(1, 2)))
        self.assertEqual(leaves[1][0], (Fraction(1, 2), Fraction(1)))
        with self.assertRaises(checker.CheckError):
            checker.parse_tree("0...", root, "test")

    def test_duplicate_keys_and_noncanonical_bytes(self):
        with self.assertRaises(checker.CheckError):
            checker.strict_load_bytes(b'{"a":1,"a":2}\n', "test")
        with self.assertRaises(checker.CheckError):
            checker.strict_load_bytes(b'{"a": 1}\n', "test")


class MutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specification = checker.Specification()
        cls.original = json.loads(LOCAL_ZERO.read_text(encoding="utf-8"))

    def assert_mutation_rejected(self, document):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutant.json"
            path.write_bytes(checker.canonical_json_bytes(document))
            with self.assertRaises(checker.CheckError):
                checker.validate_cover(path, "local/0.json", self.specification)

    def test_wrong_cover_identity_rejected(self):
        mutant = copy.deepcopy(self.original)
        mutant["name"] = "changed"
        self.assert_mutation_rejected(mutant)

    def test_missing_zoom_root_rejected(self):
        mutant = copy.deepcopy(self.original)
        mutant["zooms"].pop()
        self.assert_mutation_rejected(mutant)

    def test_tree_leaf_association_mutation_rejected(self):
        mutant = copy.deepcopy(self.original)
        mutant["zooms"][0]["tree"] += "."
        self.assert_mutation_rejected(mutant)

    def test_non_distance_factor_rejected(self):
        mutant = copy.deepcopy(self.original)
        mutant["zooms"][0]["leaves"][0]["witness"]["factor"][0] = 1
        self.assert_mutation_rejected(mutant)

    def test_illegal_delegation_rejected(self):
        mutant = copy.deepcopy(self.original)
        mutant["zooms"][0]["leaves"][0] = "delegated"
        self.assert_mutation_rejected(mutant)

    def test_out_of_range_witness_rejected(self):
        mutant = copy.deepcopy(self.original)
        mutant["zooms"][0]["leaves"][0]["witness"]["index"] = len(mutant["witnesses"])
        self.assert_mutation_rejected(mutant)


if __name__ == "__main__":
    unittest.main(verbosity=2)
