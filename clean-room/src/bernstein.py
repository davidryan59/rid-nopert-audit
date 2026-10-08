"""Independent power-to-Bernstein conversion from Article Equation (5.2)."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb
from typing import Mapping, Sequence, Tuple

from exact import Q5, ZERO
from polynomial import Exponent, Polynomial


RationalInterval = Tuple[Fraction, Fraction]


def bernstein_coefficients(
    polynomial: Polynomial,
    box: Sequence[RationalInterval],
    degrees: Sequence[int] | None = None,
) -> dict[Exponent, Q5]:
    """Return all tensor Bernstein coefficients on a rational box."""
    if len(box) != polynomial.nvars:
        raise ValueError("box dimension differs from polynomial dimension")
    for lower, upper in box:
        if lower > upper:
            raise ValueError("box interval is reversed")

    target_degrees = tuple(degrees) if degrees is not None else polynomial.degrees()
    if len(target_degrees) != polynomial.nvars:
        raise ValueError("degree vector has the wrong dimension")
    actual_degrees = polynomial.degrees()
    if any(target < actual for target, actual in zip(target_degrees, actual_degrees)):
        raise ValueError("Bernstein degree is below the power degree")

    centre = [Q5.rational(lower) for lower, _ in box]
    matrix = []
    for row, (lower, upper) in enumerate(box):
        matrix_row = [ZERO] * polynomial.nvars
        matrix_row[row] = Q5.rational(upper - lower)
        matrix.append(matrix_row)
    unit_power = polynomial.affine_substitute(centre, matrix)

    indices = list(product(*(range(degree + 1) for degree in target_degrees)))
    coefficients = {index: ZERO for index in indices}
    for power, coefficient in unit_power.terms.items():
        ranges = [range(exponent, degree + 1) for exponent, degree in zip(power, target_degrees)]
        for index in product(*ranges):
            weight = Fraction(1)
            for r, k, n in zip(index, power, target_degrees):
                weight *= Fraction(comb(r, k), comb(n, k))
            coefficients[index] += coefficient * Q5.rational(weight)
    return coefficients


def evaluate_bernstein(
    coefficients: Mapping[Exponent, Q5],
    degrees: Sequence[int],
    unit_point: Sequence[Fraction],
) -> Q5:
    """Evaluate a tensor Bernstein expansion at a rational point in [0,1]^n."""
    if len(degrees) != len(unit_point):
        raise ValueError("point dimension differs from degree dimension")
    result = ZERO
    expected = set(product(*(range(degree + 1) for degree in degrees)))
    if set(coefficients) != expected:
        raise ValueError("coefficient tensor is incomplete")
    for index, coefficient in coefficients.items():
        weight = Fraction(1)
        for i, n, y in zip(index, degrees, unit_point):
            weight *= comb(n, i) * y**i * (1 - y) ** (n - i)
        result += coefficient * Q5.rational(weight)
    return result


def all_strictly_positive(coefficients: Mapping[Exponent, Q5]) -> bool:
    return bool(coefficients) and all(coefficient.sign() > 0 for coefficient in coefficients.values())


def all_strictly_negative(coefficients: Mapping[Exponent, Q5]) -> bool:
    return bool(coefficients) and all(coefficient.sign() < 0 for coefficient in coefficients.values())
