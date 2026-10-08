from fractions import Fraction
import unittest

from exact import Q5, ZERO
from geometry import (
    arc_coordinates,
    inverse_arc_coordinates,
    inverse_pentagon_coordinates,
    pentagon_coordinates,
    rid_vertices,
    verify_arc_plane_support_equality,
    verify_pentagon_domain_identity,
)


class GeometryTests(unittest.TestCase):
    def test_vertex_set_has_sixty_points_and_central_symmetry(self):
        vertices = rid_vertices()
        self.assertEqual(len(vertices), 60)
        for vertex in vertices:
            self.assertIn(tuple(-coordinate for coordinate in vertex), vertices)

    def test_arc_planes_have_exact_support_equality(self):
        supports = verify_arc_plane_support_equality()
        self.assertEqual(supports["hole"], supports["plug_+1"])
        self.assertEqual(supports["hole"], supports["plug_-1"])

    def test_pentagon_coordinate_round_trip(self):
        for eta, xi in (
            (Q5.rational(0), Q5.rational(0)),
            (Q5.rational(Fraction(1, 37)), Q5.rational(Fraction(-2, 41))),
        ):
            s, t = inverse_pentagon_coordinates(eta, xi)
            self.assertEqual(pentagon_coordinates(s, t), (eta, xi))
            self.assertTrue(verify_pentagon_domain_identity(s, t))

    def test_arc_coordinate_round_trip(self):
        for sign in (-1, 1):
            original = (
                Q5.rational(Fraction(1, 19)),
                Q5.rational(Fraction(2, 23)),
                Q5.rational(Fraction(-3, 29)),
                Q5.rational(Fraction(5, 31)),
                Q5.rational(Fraction(-7, 43)),
            )
            view, rotation = inverse_arc_coordinates(sign, *original)
            s = view[0] / view[2]
            t = view[1] / view[2]
            self.assertEqual(arc_coordinates(sign, s, t, rotation), original)


if __name__ == "__main__":
    unittest.main()
