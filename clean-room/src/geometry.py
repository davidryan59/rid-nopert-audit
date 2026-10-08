"""Article-defined RID geometry that does not depend on serialized indices."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Iterable, Sequence, Tuple

from exact import ONE, Q5, SQRT5, ZERO


Vector3 = Tuple[Q5, Q5, Q5]

PHI = (ONE + SQRT5) / 2
PHI_BAR = ONE - PHI
A1 = (Q5.rational(-5) + 3 * SQRT5) / 10
A3 = (Q5.rational(-5) + SQRT5) / 10
ARC_ENDPOINT = SQRT5 - 2


def add(left: Vector3, right: Vector3) -> Vector3:
    return tuple(a + b for a, b in zip(left, right))  # type: ignore[return-value]


def subtract(left: Vector3, right: Vector3) -> Vector3:
    return tuple(a - b for a, b in zip(left, right))  # type: ignore[return-value]


def scale(scalar: Q5, vector: Vector3) -> Vector3:
    return tuple(scalar * value for value in vector)  # type: ignore[return-value]


def dot(left: Vector3, right: Vector3) -> Q5:
    return sum((a * b for a, b in zip(left, right)), ZERO)


def cross(left: Vector3, right: Vector3) -> Vector3:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def cyclic_permutations(vector: Vector3) -> tuple[Vector3, Vector3, Vector3]:
    x, y, z = vector
    return (vector, (y, z, x), (z, x, y))


def signed_cyclic_family(vector: Vector3) -> set[Vector3]:
    result: set[Vector3] = set()
    for permuted in cyclic_permutations(vector):
        for signs in product((-1, 1), repeat=3):
            result.add(
                tuple(Q5.rational(sign) * value for sign, value in zip(signs, permuted))  # type: ignore[arg-type]
            )
    return result


def rid_vertices() -> frozenset[Vector3]:
    """Return Equation (2.1) as a set, without assigning JSON indices."""
    families = [
        (ONE, ONE, PHI**3),
        (PHI**2, PHI, 2 * PHI),
        (2 + PHI, ZERO, PHI**2),
    ]
    vertices: set[Vector3] = set()
    for family in families:
        vertices.update(signed_cyclic_family(family))
    if len(vertices) != 60:
        raise ArithmeticError(f"Equation (2.1) produced {len(vertices)} vertices, expected 60")
    return frozenset(vertices)


def rotation_numerator(rotation: Vector3, vector: Vector3) -> Vector3:
    norm_square = dot(rotation, rotation)
    return add(
        add(scale(ONE - norm_square, vector), scale(2 * dot(rotation, vector), rotation)),
        scale(Q5.rational(2), cross(rotation, vector)),
    )


def rotate(rotation: Vector3, vector: Vector3) -> Vector3:
    denominator = ONE + dot(rotation, rotation)
    return tuple(value / denominator for value in rotation_numerator(rotation, vector))  # type: ignore[return-value]


def arc_base_rotation(sign: int) -> Vector3:
    if sign not in (-1, 1):
        raise ValueError("arc sign must be -1 or 1")
    return (sign * A1, ZERO, sign * A3)


def verify_arc_plane_support_equality() -> dict[str, Q5]:
    """Recompute the finite equality used in Lemma 9.1 for both planes."""
    vertices = rid_vertices()
    hole_support = max(vertex[1] for vertex in vertices)
    expected = 2 + SQRT5
    if hole_support != expected:
        raise ArithmeticError("Equation (2.1) has an unexpected e2 support")
    result = {"hole": hole_support}
    for sign in (-1, 1):
        rotation = arc_base_rotation(sign)
        plug_support = max(rotate(rotation, vertex)[1] for vertex in vertices)
        if plug_support != hole_support:
            raise ArithmeticError(f"arc plane {sign:+d} fails the support equality")
        result[f"plug_{sign:+d}"] = plug_support
    return result


def pentagon_coordinates(s: Q5, t: Q5) -> tuple[Q5, Q5]:
    eta = s + PHI_BAR * t
    xi = s + PHI * t + PHI_BAR
    return eta, xi


def inverse_pentagon_coordinates(eta: Q5, xi: Q5) -> tuple[Q5, Q5]:
    s0 = (Q5.rational(-5) + 3 * SQRT5) / 10
    t0 = (Q5.rational(5) - SQRT5) / 10
    s = s0 + (PHI * eta - PHI_BAR * xi) / SQRT5
    t = t0 + (xi - eta) / SQRT5
    return s, t


def verify_pentagon_domain_identity(s: Q5, t: Q5) -> bool:
    _, xi = pentagon_coordinates(s, t)
    return PHI * xi == PHI * s + PHI**2 * t - 1


def arc_coordinates(sign: int, s: Q5, t: Q5, rotation: Vector3) -> tuple[Q5, Q5, Q5, Q5, Q5]:
    if sign not in (-1, 1):
        raise ValueError("arc sign must be -1 or 1")
    denominator = 2 + s
    e = (1 - 2 * s) / denominator
    v = 5 * t / denominator
    theta = rotation[1]
    zeta1 = rotation[0] - sign * (A1 + A3 * theta)
    zeta3 = rotation[2] - sign * (A3 - A1 * theta)
    return e, v, theta, zeta1, zeta3


def inverse_arc_coordinates(
    sign: int,
    e: Q5,
    v: Q5,
    theta: Q5,
    zeta1: Q5,
    zeta3: Q5,
) -> tuple[Vector3, Vector3]:
    if sign not in (-1, 1):
        raise ValueError("arc sign must be -1 or 1")
    view = (1 - 2 * e, v, 2 + e)
    rotation = (
        sign * A1 + sign * A3 * theta + zeta1,
        theta,
        sign * A3 - sign * A1 * theta + zeta3,
    )
    return view, rotation
