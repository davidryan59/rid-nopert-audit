#!/usr/bin/env python3
"""Independent exact checker for the rid-cover/1 certificate format."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


SPEC_DIR = Path("/Users/davidryan/code/projects/rid-nopert-audit/specification")
INPUT_DIR = Path("/Users/davidryan/code/projects/rid-nopert-audit/clean-room/inputs")
ZERO_EXP = (0, 0, 0, 0, 0)
RATIONAL_RE = re.compile(r"^(0|-?[1-9][0-9]*|-?[1-9][0-9]*/(?:[2-9]|[1-9][0-9]+))$")


class CheckError(Exception):
    """A closed-check failure with a stable diagnostic."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckError(message)


def parse_rational(value: Any, where: str = "rational") -> Fraction:
    require(type(value) is str and RATIONAL_RE.fullmatch(value) is not None,
            f"{where}: non-canonical rational")
    if "/" in value:
        numerator, denominator = value.split("/")
        fraction = Fraction(int(numerator), int(denominator))
        require(fraction.denominator != 1, f"{where}: integer encoded as fraction")
        require(math.gcd(abs(int(numerator)), int(denominator)) == 1,
                f"{where}: reducible fraction")
        return fraction
    return Fraction(int(value))


def rational_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


@dataclass(frozen=True)
class K:
    """An exact element a + b*sqrt(5)."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __add__(self, other: Any) -> "K":
        other = as_k(other)
        return K(self.a + other.a, self.b + other.b)

    __radd__ = __add__

    def __neg__(self) -> "K":
        return K(-self.a, -self.b)

    def __sub__(self, other: Any) -> "K":
        return self + (-as_k(other))

    def __rsub__(self, other: Any) -> "K":
        return as_k(other) - self

    def __mul__(self, other: Any) -> "K":
        other = as_k(other)
        return K(self.a * other.a + 5 * self.b * other.b,
                 self.a * other.b + self.b * other.a)

    __rmul__ = __mul__

    def inverse(self) -> "K":
        norm = self.a * self.a - 5 * self.b * self.b
        require(norm != 0, "division by zero in Q(sqrt(5))")
        return K(self.a / norm, -self.b / norm)

    def __truediv__(self, other: Any) -> "K":
        return self * as_k(other).inverse()

    def sign(self) -> int:
        if self.a == 0:
            return (self.b > 0) - (self.b < 0)
        if self.b == 0:
            return (self.a > 0) - (self.a < 0)
        if (self.a > 0) == (self.b > 0):
            return 1 if self.a > 0 else -1
        comparison = self.a * self.a - 5 * self.b * self.b
        if comparison > 0:
            return 1 if self.a > 0 else -1
        return 1 if self.b > 0 else -1

    def is_zero(self) -> bool:
        return self.a == 0 and self.b == 0


def as_k(value: Any) -> K:
    if isinstance(value, K):
        return value
    if isinstance(value, Fraction):
        return K(value)
    if type(value) is int:
        return K(Fraction(value))
    raise TypeError(f"cannot convert {type(value).__name__} to K")


def parse_k(value: Any, where: str = "Q(sqrt(5)) number") -> K:
    require(type(value) is list and len(value) == 2, f"{where}: expected two elements")
    return K(parse_rational(value[0], f"{where}[0]"),
             parse_rational(value[1], f"{where}[1]"))


Poly = dict


def pclean(poly: Poly) -> Poly:
    return {exponents: coefficient for exponents, coefficient in poly.items()
            if not coefficient.is_zero()}


def pconst(value: Any) -> Poly:
    coefficient = as_k(value)
    return {} if coefficient.is_zero() else {ZERO_EXP: coefficient}


def pvar(index: int) -> Poly:
    exponents = [0] * 5
    exponents[index] = 1
    return {tuple(exponents): K(Fraction(1))}


def padd(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for exponents, coefficient in right.items():
        result[exponents] = result.get(exponents, K()) + coefficient
        if result[exponents].is_zero():
            del result[exponents]
    return result


def pneg(poly: Poly) -> Poly:
    return {exponents: -coefficient for exponents, coefficient in poly.items()}


def psub(left: Poly, right: Poly) -> Poly:
    return padd(left, pneg(right))


def pscale(poly: Poly, scalar: Any) -> Poly:
    scalar = as_k(scalar)
    if scalar.is_zero():
        return {}
    return pclean({exponents: coefficient * scalar for exponents, coefficient in poly.items()})


def pmul(left: Poly, right: Poly) -> Poly:
    if not left or not right:
        return {}
    result: Poly = {}
    for left_exp, left_coefficient in left.items():
        for right_exp, right_coefficient in right.items():
            exponents = tuple(a + b for a, b in zip(left_exp, right_exp))
            result[exponents] = result.get(exponents, K()) + left_coefficient * right_coefficient
    return pclean(result)


def ppow(poly: Poly, exponent: int) -> Poly:
    require(type(exponent) is int and exponent >= 0, "invalid polynomial exponent")
    result = pconst(1)
    base = poly
    power = exponent
    while power:
        if power & 1:
            result = pmul(result, base)
        power //= 2
        if power:
            base = pmul(base, base)
    return result


def pdot(left: list[Poly], right: list[Poly]) -> Poly:
    require(len(left) == len(right), "vector length mismatch")
    result: Poly = {}
    for a, b in zip(left, right):
        result = padd(result, pmul(a, b))
    return result


def pcross(left: list[Poly], right: list[Poly]) -> list[Poly]:
    require(len(left) == len(right) == 3, "cross product requires three components")
    return [
        psub(pmul(left[1], right[2]), pmul(left[2], right[1])),
        psub(pmul(left[2], right[0]), pmul(left[0], right[2])),
        psub(pmul(left[0], right[1]), pmul(left[1], right[0])),
    ]


def peval(poly: Poly, point: tuple[Fraction, ...]) -> K:
    result = K()
    for exponents, coefficient in poly.items():
        multiplier = Fraction(1)
        for coordinate, exponent in zip(point, exponents):
            multiplier *= coordinate ** exponent
        result += coefficient * multiplier
    return result


def pdivide_monomial(poly: Poly, factor: tuple[int, ...], where: str) -> Poly:
    result: Poly = {}
    for exponents, coefficient in poly.items():
        require(all(exponents[i] >= factor[i] for i in range(5)),
                f"{where}: witness polynomial is not divisible by factor {list(factor)}")
        divided = tuple(exponents[i] - factor[i] for i in range(5))
        result[divided] = coefficient
    return result


def polynomial_degrees(poly: Poly) -> tuple[int, ...]:
    if not poly:
        return ZERO_EXP
    return tuple(max(exponents[i] for exponents in poly) for i in range(5))


def bernstein_coefficients(poly: Poly,
                           cell: tuple[tuple[Fraction, Fraction], ...]) -> Iterable[tuple[tuple[int, ...], K]]:
    """Convert a power polynomial to the tensor Bernstein basis on cell."""
    transformed: Poly = {}
    for exponents, coefficient in poly.items():
        partial: Poly = {ZERO_EXP: coefficient}
        for axis, exponent in enumerate(exponents):
            if exponent == 0:
                continue
            lo, hi = cell[axis]
            width = hi - lo
            expansion: Poly = {}
            for power in range(exponent + 1):
                out_exp = [0] * 5
                out_exp[axis] = power
                scalar = Fraction(math.comb(exponent, power)) * lo ** (exponent - power) * width ** power
                if scalar:
                    expansion[tuple(out_exp)] = K(scalar)
            partial = pmul(partial, expansion)
        transformed = padd(transformed, partial)

    degrees = polynomial_degrees(transformed)
    for index in itertools.product(*(range(degree + 1) for degree in degrees)):
        coefficient = K()
        for powers, power_coefficient in transformed.items():
            if all(powers[axis] <= index[axis] for axis in range(5)):
                multiplier = Fraction(1)
                for axis in range(5):
                    multiplier *= Fraction(math.comb(index[axis], powers[axis]),
                                           math.comb(degrees[axis], powers[axis]))
                coefficient += power_coefficient * multiplier
        yield index, coefficient


def require_negative_bernstein(poly: Poly,
                               cell: tuple[tuple[Fraction, Fraction], ...], where: str) -> int:
    count = 0
    for index, coefficient in bernstein_coefficients(poly, cell):
        count += 1
        require(coefficient.sign() < 0,
                f"{where}: Bernstein coefficient {list(index)} is not strictly negative")
    return count


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CheckError(f"repeated JSON key {key!r}")
        result[key] = value
    return result


def reject_float(value: str) -> Any:
    raise CheckError(f"JSON non-integer number {value!r}")


def reject_constant(value: str) -> Any:
    raise CheckError(f"JSON non-finite number {value!r}")


def canonical_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        return (text + "\n").encode("utf-8")
    except (UnicodeError, ValueError, TypeError) as error:
        raise CheckError(f"cannot canonically encode JSON: {error}") from error


def strict_load_bytes(data: bytes, where: str) -> Any:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CheckError(f"{where}: invalid UTF-8") from error
    try:
        value = json.loads(text, object_pairs_hook=strict_object,
                           parse_float=reject_float, parse_constant=reject_constant)
    except CheckError:
        raise
    except json.JSONDecodeError as error:
        raise CheckError(f"{where}: invalid JSON at byte-like character {error.pos}: {error.msg}") from error
    require(canonical_json_bytes(value) == data, f"{where}: bytes are not canonical JSON")
    return value


def strict_load(path: Path) -> Any:
    return strict_load_bytes(path.read_bytes(), str(path))


def exact_keys(value: Any, keys: list[str], where: str) -> dict[str, Any]:
    require(type(value) is dict, f"{where}: expected object")
    require(list(value.keys()) == keys, f"{where}: expected fields in order {keys}")
    return value


def exact_list(value: Any, length: int | None, where: str) -> list[Any]:
    require(type(value) is list, f"{where}: expected array")
    if length is not None:
        require(len(value) == length, f"{where}: expected {length} elements")
    return value


def exact_int(value: Any, lo: int, hi: int, where: str) -> int:
    require(type(value) is int and lo <= value <= hi, f"{where}: integer outside [{lo},{hi}]")
    return value


def face_list(box: list[list[int]]) -> list[dict[str, int]]:
    result = []
    for axis, interval in enumerate(box):
        if interval[0] != 0:
            result.append({"axis": axis, "side": -1})
        if interval[1] != 0:
            result.append({"axis": axis, "side": 1})
    return result


def face_text(face: dict[str, int]) -> str:
    return f"{face['axis']}{'-' if face['side'] < 0 else '+'}"


def validate_unit_box(value: Any, where: str) -> list[list[int]]:
    box = exact_list(value, None, where)
    require(1 <= len(box) <= 4, f"{where}: unit box dimension outside [1,4]")
    for axis, interval in enumerate(box):
        require(type(interval) is list and interval in [[-1, 0], [-1, 1], [0, 1]],
                f"{where}[{axis}]: invalid unit interval")
        require(all(type(endpoint) is int for endpoint in interval),
                f"{where}[{axis}]: Boolean endpoint")
    return box


def validate_face(value: Any, dimension: int, where: str) -> dict[str, int]:
    face = exact_keys(value, ["axis", "side"], where)
    exact_int(face["axis"], 0, dimension - 1, f"{where}.axis")
    require(type(face["side"]) is int and face["side"] in (-1, 1), f"{where}.side: invalid side")
    return face


def matrix_nonsingular(matrix: list[list[K]]) -> bool:
    work = [row[:] for row in matrix]
    size = len(work)
    for column in range(size):
        pivot = next((row for row in range(column, size) if not work[row][column].is_zero()), None)
        if pivot is None:
            return False
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        for j in range(column, size):
            work[column][j] = work[column][j] / pivot_value
        for row in range(column + 1, size):
            factor = work[row][column]
            if factor.is_zero():
                continue
            for j in range(column, size):
                work[row][j] = work[row][j] - factor * work[column][j]
    return True


def validate_parameters(value: Any, where: str, enforce_order: bool = True) -> dict[str, Any]:
    expected = ["coordinates", "centre", "map", "shape", "beyond"]
    if enforce_order:
        parameters = exact_keys(value, expected, where)
    else:
        require(type(value) is dict and set(value) == set(expected), f"{where}: wrong parameter fields")
        parameters = value

    coordinates = parameters["coordinates"]
    if type(coordinates) is dict:
        coordinates = exact_keys(coordinates, ["arc-plane"], f"{where}.coordinates")
        require(coordinates["arc-plane"] in ("plus", "minus"), f"{where}.coordinates: invalid arc plane")
    else:
        require(coordinates == "configuration", f"{where}.coordinates: invalid coordinate system")

    centre_json = exact_list(parameters["centre"], 5, f"{where}.centre")
    centre = [parse_k(item, f"{where}.centre[{i}]") for i, item in enumerate(centre_json)]
    matrix_json = exact_list(parameters["map"], 5, f"{where}.map")
    matrix: list[list[K]] = []
    for row_index, row in enumerate(matrix_json):
        row = exact_list(row, 5, f"{where}.map[{row_index}]")
        matrix.append([parse_k(item, f"{where}.map[{row_index}][{column}]")
                       for column, item in enumerate(row)])
    require(matrix_nonsingular(matrix), f"{where}.map: singular affine map")

    shape = parameters["shape"]
    require(type(shape) is dict and len(shape) == 1, f"{where}.shape: expected one shape")
    if "tube" in shape:
        tube = exact_keys(shape["tube"], ["base", "offset", "radius"], f"{where}.shape.tube")
        base = exact_list(tube["base"], None, f"{where}.shape.tube.base")
        require(1 <= len(base) <= 4, f"{where}.shape.tube.base: invalid dimension")
        for axis, interval in enumerate(base):
            interval = exact_list(interval, 2, f"{where}.shape.tube.base[{axis}]")
            lo = parse_rational(interval[0], f"{where}.shape.tube.base[{axis}][0]")
            hi = parse_rational(interval[1], f"{where}.shape.tube.base[{axis}][1]")
            require(lo < hi, f"{where}.shape.tube.base[{axis}]: non-positive width")
        offset = validate_unit_box(tube["offset"], f"{where}.shape.tube.offset")
        radius = parse_rational(tube["radius"], f"{where}.shape.tube.radius")
        require(radius > 0, f"{where}.shape.tube.radius: must be positive")
        require(len(base) + len(offset) == 5, f"{where}.shape.tube: dimensions do not sum to five")
    elif "point" in shape:
        point = exact_keys(shape["point"],
                           ["base", "offset", "radii", "radius", "ratio", "window"],
                           f"{where}.shape.point")
        base = validate_unit_box(point["base"], f"{where}.shape.point.base")
        offset = validate_unit_box(point["offset"], f"{where}.shape.point.offset")
        require(len(base) + len(offset) == 5, f"{where}.shape.point: dimensions do not sum to five")
        radii = exact_list(point["radii"], None, f"{where}.shape.point.radii")
        require(len(radii) == len(face_list(base)), f"{where}.shape.point.radii: face count mismatch")
        for index, radius_text in enumerate(radii):
            require(parse_rational(radius_text, f"{where}.shape.point.radii[{index}]") > 0,
                    f"{where}.shape.point.radii[{index}]: must be positive")
        require(parse_rational(point["radius"], f"{where}.shape.point.radius") > 0,
                f"{where}.shape.point.radius: must be positive")
        require(parse_rational(point["ratio"], f"{where}.shape.point.ratio") > 0,
                f"{where}.shape.point.ratio: must be positive")
        window = point["window"]
        if window is not None:
            window_keys = ["faces", "shear", "radius"]
            if enforce_order:
                window = exact_keys(window, window_keys, f"{where}.shape.point.window")
            else:
                require(type(window) is dict and set(window) == set(window_keys),
                        f"{where}.shape.point.window: wrong fields")
            window_faces = exact_list(window["faces"], None, f"{where}.shape.point.window.faces")
            require(window_faces, f"{where}.shape.point.window.faces: empty")
            seen_faces: set[tuple[int, int]] = set()
            permitted_faces = {(face["axis"], face["side"]) for face in face_list(base)}
            for index, face in enumerate(window_faces):
                parsed = validate_face(face, len(base), f"{where}.shape.point.window.faces[{index}]")
                key = parsed["axis"], parsed["side"]
                require(key not in seen_faces, f"{where}.shape.point.window.faces: duplicate")
                require(key in permitted_faces, f"{where}.shape.point.window.faces: face outside base box")
                seen_faces.add(key)
            shear = exact_list(window["shear"], len(offset), f"{where}.shape.point.window.shear")
            for row_index, row in enumerate(shear):
                row = exact_list(row, len(base), f"{where}.shape.point.window.shear[{row_index}]")
                for column, entry in enumerate(row):
                    parse_rational(entry, f"{where}.shape.point.window.shear[{row_index}][{column}]")
            require(parse_rational(window["radius"], f"{where}.shape.point.window.radius") > 0,
                    f"{where}.shape.point.window.radius: must be positive")
    else:
        raise CheckError(f"{where}.shape: unknown shape")

    beyond = parameters["beyond"]
    if beyond is not None:
        beyond = exact_keys(beyond, ["axis", "inequality"], f"{where}.beyond")
        exact_int(beyond["axis"], 0, 4, f"{where}.beyond.axis")
        exact_int(beyond["inequality"], 0, 72, f"{where}.beyond.inequality")
    return parameters


def interval_text(interval: list[int]) -> list[str]:
    return [str(interval[0]), str(interval[1])]


def derive_zooms(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    shape = parameters["shape"]
    zooms: list[dict[str, Any]] = []
    if "tube" in shape:
        tube = shape["tube"]
        base = tube["base"]
        offset = tube["offset"]
        k = len(base)
        for offset_face in face_list(offset):
            free_offset = [axis for axis in range(len(offset)) if axis != offset_face["axis"]]
            root = [list(interval) for interval in base]
            root.append(["0", tube["radius"]])
            root.extend(interval_text(offset[axis]) for axis in free_offset)
            roles = [f"base[{axis}]" for axis in range(k)] + ["delta"]
            roles.extend(f"offset-unit[{axis}]" for axis in free_offset)
            zooms.append({
                "base_face": None,
                "distance_variables": [k],
                "family": "tube",
                "index": len(zooms),
                "name": f"T o{face_text(offset_face)}",
                "offset_face": offset_face,
                "root": root,
                "variable_roles": roles,
            })
        return zooms

    point = shape["point"]
    base = point["base"]
    offset = point["offset"]
    base_faces = face_list(base)
    offset_faces = face_list(offset)
    radii = point["radii"]
    for base_index, base_face in enumerate(base_faces):
        for offset_face in offset_faces:
            free_base = [axis for axis in range(len(base)) if axis != base_face["axis"]]
            free_offset = [axis for axis in range(len(offset)) if axis != offset_face["axis"]]
            root = [["0", radii[base_index]], ["0", point["ratio"]]]
            root.extend(interval_text(base[axis]) for axis in free_base)
            root.extend(interval_text(offset[axis]) for axis in free_offset)
            roles = ["mu", "rho"]
            roles.extend(f"base-unit[{axis}]" for axis in free_base)
            roles.extend(f"offset-unit[{axis}]" for axis in free_offset)
            zooms.append({
                "base_face": base_face,
                "distance_variables": [0, 1],
                "family": "a",
                "index": len(zooms),
                "name": f"A b{face_text(base_face)} o{face_text(offset_face)}",
                "offset_face": offset_face,
                "root": root,
                "variable_roles": roles,
            })
    inverse_ratio = Fraction(1, 1) / parse_rational(point["ratio"])
    for offset_face in offset_faces:
        free_offset = [axis for axis in range(len(offset)) if axis != offset_face["axis"]]
        root = [["0", point["radius"]]]
        for interval in base:
            root.append([rational_text(Fraction(interval[0]) * inverse_ratio),
                         rational_text(Fraction(interval[1]) * inverse_ratio)])
        root.extend(interval_text(offset[axis]) for axis in free_offset)
        roles = ["delta"]
        roles.extend(f"base-cone[{axis}]" for axis in range(len(base)))
        roles.extend(f"offset-unit[{axis}]" for axis in free_offset)
        zooms.append({
            "base_face": None,
            "distance_variables": [0],
            "family": "b",
            "index": len(zooms),
            "name": f"B o{face_text(offset_face)}",
            "offset_face": offset_face,
            "root": root,
            "variable_roles": roles,
        })
    window = point["window"]
    if window is not None:
        radius_by_face = {(face["axis"], face["side"]): radii[index]
                          for index, face in enumerate(base_faces)}
        for base_face in window["faces"]:
            for offset_face in offset_faces:
                free_base = [axis for axis in range(len(base)) if axis != base_face["axis"]]
                free_offset = [axis for axis in range(len(offset)) if axis != offset_face["axis"]]
                root = [["0", radius_by_face[(base_face["axis"], base_face["side"])]],
                        ["0", window["radius"]]]
                root.extend(interval_text(base[axis]) for axis in free_base)
                root.extend(interval_text(offset[axis]) for axis in free_offset)
                roles = ["mu", "rho-prime"]
                roles.extend(f"base-unit[{axis}]" for axis in free_base)
                roles.extend(f"offset-unit[{axis}]" for axis in free_offset)
                zooms.append({
                    "base_face": base_face,
                    "distance_variables": [0, 1],
                    "family": "sheared-a",
                    "index": len(zooms),
                    "name": f"A' b{face_text(base_face)} o{face_text(offset_face)}",
                    "offset_face": offset_face,
                    "root": root,
                    "variable_roles": roles,
                })
    return zooms


def unit_vector(box: list[list[int]], face: dict[str, int], variables: Iterable[Poly]) -> list[Poly]:
    iterator = iter(variables)
    result = []
    for axis in range(len(box)):
        if axis == face["axis"]:
            result.append(pconst(face["side"]))
        else:
            result.append(next(iterator))
    return result


@dataclass
class ZoomMap:
    z: list[Poly]
    base_unit: list[Poly] | None
    offset_unit: list[Poly]
    mu: Poly | None
    rho: Poly | None


def build_zoom_map(parameters: dict[str, Any], zoom: dict[str, Any]) -> ZoomMap:
    variables = [pvar(i) for i in range(5)]
    shape = parameters["shape"]
    family = zoom["family"]
    if family == "tube":
        tube = shape["tube"]
        k = len(tube["base"])
        offset_unit = unit_vector(tube["offset"], zoom["offset_face"], variables[k + 1:])
        z_base = variables[:k]
        z_offset = [pmul(variables[k], item) for item in offset_unit]
        return ZoomMap(z_base + z_offset, None, offset_unit, None, variables[k])

    point = shape["point"]
    k = len(point["base"])
    if family in ("a", "sheared-a"):
        base_unit = unit_vector(point["base"], zoom["base_face"], variables[2:2 + k - 1])
        offset_unit = unit_vector(point["offset"], zoom["offset_face"], variables[2 + k - 1:])
        mu, rho = variables[0], variables[1]
        z_base = [pmul(mu, item) for item in base_unit]
        z_offset = [pmul(pmul(mu, rho), item) for item in offset_unit]
        if family == "sheared-a":
            shear = point["window"]["shear"]
            for row in range(len(z_offset)):
                correction: Poly = {}
                for column in range(k):
                    correction = padd(correction,
                                      pscale(z_base[column], parse_rational(shear[row][column])))
                z_offset[row] = psub(z_offset[row], correction)
        return ZoomMap(z_base + z_offset, base_unit, offset_unit, mu, rho)

    require(family == "b", f"unknown zoom family {family!r}")
    delta = variables[0]
    base_vector = variables[1:1 + k]
    offset_unit = unit_vector(point["offset"], zoom["offset_face"], variables[1 + k:])
    z_base = [pmul(delta, item) for item in base_vector]
    z_offset = [pmul(delta, item) for item in offset_unit]
    return ZoomMap(z_base + z_offset, base_vector, offset_unit, delta, None)


def adapted_polynomials(parameters: dict[str, Any], z: list[Poly]) -> list[Poly]:
    centre = [parse_k(item) for item in parameters["centre"]]
    matrix = [[parse_k(item) for item in row] for row in parameters["map"]]
    result = []
    for row in range(5):
        value = pconst(centre[row])
        for column in range(5):
            value = padd(value, pscale(z[column], matrix[row][column]))
        result.append(value)
    return result


def configuration_polynomials(parameters: dict[str, Any], z: list[Poly]) -> tuple[list[Poly], list[Poly]]:
    x = adapted_polynomials(parameters, z)
    if parameters["coordinates"] == "configuration":
        return [x[0], x[1], pconst(1)], x[2:5]
    sign = 1 if parameters["coordinates"]["arc-plane"] == "plus" else -1
    e, v, theta, zeta1, zeta3 = x
    a1 = K(Fraction(-1, 2), Fraction(3, 10))
    a3 = K(Fraction(-1, 2), Fraction(1, 10))
    r_a = [a1, K(), a3]
    w = [sign * a3, K(Fraction(1)), -sign * a1]
    u = [padd(pconst(1), pscale(e, -2)), v, padd(pconst(2), e)]
    r = []
    additions = [zeta1, {}, zeta3]
    for axis in range(3):
        value = padd(pconst(sign * r_a[axis]), pscale(theta, w[axis]))
        value = padd(value, additions[axis])
        r.append(value)
    return u, r


def constant_vector(values: list[K]) -> list[Poly]:
    return [pconst(value) for value in values]


def gap_normal(witness: dict[str, Any], u: list[Poly], vertices: list[list[K]]) -> tuple[list[Poly], list[K], list[K]]:
    if "edge" in witness:
        start, end = witness["edge"]
        direction = [vertices[end][axis] - vertices[start][axis] for axis in range(3)]
        normal = pcross(u, constant_vector(direction))
        return normal, vertices[start], vertices[witness["vertex"]]
    direction = [parse_k(item) for item in witness["direction"]]
    normal = [pmul(pconst(direction[0]), u[2]),
              pmul(pconst(direction[1]), u[2]),
              pneg(padd(pmul(pconst(direction[0]), u[0]),
                        pmul(pconst(direction[1]), u[1])))]
    return normal, vertices[witness["contact"]], vertices[witness["vertex"]]


def gap_polynomial(witness: dict[str, Any], u: list[Poly], r: list[Poly],
                   vertices: list[list[K]]) -> tuple[Poly, list[Poly]]:
    normal, hole_vertex, plug_vertex = gap_normal(witness, u, vertices)
    r_squared = pdot(r, r)
    denominator = padd(pconst(1), r_squared)
    r_dot_vertex = pdot(r, constant_vector(plug_vertex))
    r_cross_vertex = pcross(r, constant_vector(plug_vertex))
    rotated = []
    for axis in range(3):
        component = pscale(psub(pconst(1), r_squared), plug_vertex[axis])
        component = padd(component, pscale(pmul(r[axis], r_dot_vertex), 2))
        component = padd(component, pscale(r_cross_vertex[axis], 2))
        rotated.append(component)
    first = pmul(denominator, pdot(normal, constant_vector(hole_vertex)))
    return psub(first, pdot(normal, rotated)), normal


def domain_polynomial(row: dict[str, Any], u: list[Poly], r: list[Poly]) -> Poly:
    degree = row["homogeneous_view_degree"]
    result: Poly = {}
    for term in row["terms"]:
        exponents = term["exponents"]
        u3_exponent = degree - exponents[0] - exponents[1]
        require(u3_exponent >= 0, f"inequality {row['index']}: invalid homogeneous degree")
        value = pconst(parse_k(term["coefficient"]))
        value = pmul(value, ppow(u[0], exponents[0]))
        value = pmul(value, ppow(u[1], exponents[1]))
        value = pmul(value, ppow(u[2], u3_exponent))
        for axis in range(3):
            value = pmul(value, ppow(r[axis], exponents[axis + 2]))
        result = padd(result, value)
    return result


def witness_polynomial(witness: dict[str, Any], u: list[Poly], r: list[Poly],
                       specification: "Specification") -> tuple[Poly, list[Poly] | None]:
    if "inequality" in witness:
        q = domain_polynomial(specification.inequality_rows[witness["inequality"]], u, r)
        return pneg(q), None
    return gap_polynomial(witness, u, r, specification.vertices)


def corners(cell: tuple[tuple[Fraction, Fraction], ...]) -> Iterable[tuple[Fraction, ...]]:
    return itertools.product(*((interval[0], interval[1]) for interval in cell))


def validate_corner_conditions(u: list[Poly], normal: list[Poly] | None,
                               hole_vertex: list[K] | None, vertices: list[list[K]],
                               cell: tuple[tuple[Fraction, Fraction], ...], where: str) -> int:
    count = 0
    for corner in corners(cell):
        count += 1
        require(peval(u[2], corner).sign() > 0, f"{where}: u3 is not positive at a cell corner")
        if normal is None:
            continue
        normal_value = [peval(component, corner) for component in normal]
        if all(component.is_zero() for component in normal_value):
            continue
        assert hole_vertex is not None
        for vertex_index, vertex in enumerate(vertices):
            support = K()
            for axis in range(3):
                support += normal_value[axis] * (hole_vertex[axis] - vertex[axis])
            require(support.sign() >= 0,
                    f"{where}: support fails at corner for vertex {vertex_index}")
    return count


def parse_tree(tree: str, root: tuple[tuple[Fraction, Fraction], ...], where: str) -> list[tuple[tuple[Fraction, Fraction], ...]]:
    require(type(tree) is str and tree, f"{where}: tree must be a nonempty string")
    require(all(character in "01234." for character in tree), f"{where}: invalid tree byte")
    position = 0
    leaves: list[tuple[tuple[Fraction, Fraction], ...]] = []

    def descend(cell: tuple[tuple[Fraction, Fraction], ...]) -> None:
        nonlocal position
        require(position < len(tree), f"{where}: early tree termination")
        character = tree[position]
        position += 1
        if character == ".":
            leaves.append(cell)
            return
        axis = int(character)
        lo, hi = cell[axis]
        midpoint = (lo + hi) / 2
        lower = list(cell)
        upper = list(cell)
        lower[axis] = (lo, midpoint)
        upper[axis] = (midpoint, hi)
        descend(tuple(lower))
        descend(tuple(upper))

    descend(root)
    require(position == len(tree), f"{where}: trailing tree bytes")
    return leaves


def parse_root(root: Any, where: str) -> tuple[tuple[Fraction, Fraction], ...]:
    root = exact_list(root, 5, where)
    intervals = []
    for axis, interval in enumerate(root):
        interval = exact_list(interval, 2, f"{where}[{axis}]")
        lo = parse_rational(interval[0], f"{where}[{axis}][0]")
        hi = parse_rational(interval[1], f"{where}[{axis}][1]")
        require(lo < hi, f"{where}[{axis}]: non-positive width")
        intervals.append((lo, hi))
    return tuple(intervals)


def interval_range(poly: Poly, cell: tuple[tuple[Fraction, Fraction], ...], where: str) -> tuple[K, K]:
    require(all(exponent <= 1 for term in poly for exponent in term),
            f"{where}: interval polynomial is not multilinear")
    values = [peval(poly, corner) for corner in corners(cell)]
    lo = min(values, key=lambda value: (value.sign(), value.a, value.b))
    hi = max(values, key=lambda value: (value.sign(), value.a, value.b))
    # The key above is not a total algebraic order. Select by exact pairwise comparison.
    lo = values[0]
    hi = values[0]
    for value in values[1:]:
        if (value - lo).sign() < 0:
            lo = value
        if (value - hi).sign() > 0:
            hi = value
    return lo, hi


def covered_bounds(parameters: dict[str, Any]) -> list[tuple[Fraction, Fraction]]:
    shape = parameters["shape"]
    if "tube" in shape:
        tube = shape["tube"]
        result = [(parse_rational(interval[0]), parse_rational(interval[1])) for interval in tube["base"]]
        radius = parse_rational(tube["radius"])
        result.extend((Fraction(interval[0]) * radius, Fraction(interval[1]) * radius)
                      for interval in tube["offset"])
        return result
    point = shape["point"]
    radii_by_face = {(face["axis"], face["side"]): parse_rational(point["radii"][index])
                     for index, face in enumerate(face_list(point["base"]))}
    result = []
    for axis, interval in enumerate(point["base"]):
        lo = Fraction(0) if interval[0] == 0 else -radii_by_face[(axis, -1)]
        hi = Fraction(0) if interval[1] == 0 else radii_by_face[(axis, 1)]
        result.append((lo, hi))
    radius = parse_rational(point["radius"])
    result.extend((Fraction(interval[0]) * radius, Fraction(interval[1]) * radius)
                  for interval in point["offset"])
    return result


class Specification:
    def __init__(self, specification_dir: Path = SPEC_DIR):
        self.directory = specification_dir
        with (specification_dir / "vertices.json").open("r", encoding="utf-8") as handle:
            vertex_data = json.load(handle)
        with (specification_dir / "domain-inequalities.json").open("r", encoding="utf-8") as handle:
            inequality_data = json.load(handle)
        with (specification_dir / "cover-inventory.json").open("r", encoding="utf-8") as handle:
            inventory_data = json.load(handle)
        self.vertices = self._validate_vertices(vertex_data)
        self.inequality_rows = self._validate_inequalities(inequality_data)
        self.inventory = self._validate_inventory(inventory_data)
        self.cover_by_path = {cover["path"]: cover for cover in self.inventory["covers"]}

    @staticmethod
    def _validate_vertices(data: Any) -> list[list[K]]:
        require(type(data) is dict and data.get("format") == "rid-cover-vertices/1",
                "vertices table: invalid format")
        require(data.get("field") == "Q(sqrt5)" and data.get("coordinate_order") == ["x", "y", "z"],
                "vertices table: invalid metadata")
        rows = data.get("vertices")
        require(type(rows) is list and len(rows) == 60, "vertices table: expected 60 rows")
        parsed = []
        for index, row in enumerate(rows):
            require(type(row) is dict and set(row) == {"index", "coordinates"},
                    f"vertices table row {index}: invalid fields")
            require(row["index"] == index, f"vertices table row {index}: wrong index")
            coordinates = exact_list(row["coordinates"], 3, f"vertices table row {index}.coordinates")
            parsed.append([parse_k(value, f"vertices table row {index}") for value in coordinates])

        seeds = [((2, 0), (2, 0), (4, 2)),
                 ((3, 1), (1, 1), (2, 2)),
                 ((5, 1), (0, 0), (3, 1))]
        generated: set[tuple[tuple[int, int], ...]] = set()
        for seed in seeds:
            for signs in itertools.product((-1, 1), repeat=3):
                signed = tuple((signs[i] * seed[i][0], signs[i] * seed[i][1]) for i in range(3))
                for shift in range(3):
                    generated.add(signed[shift:] + signed[:shift])
        ordered = sorted(generated)
        require(len(ordered) == 60, "vertex generation rule did not produce 60 vertices")
        regenerated = [[K(Fraction(a, 2), Fraction(b, 2)) for a, b in row] for row in ordered]
        require(parsed == regenerated, "vertices table does not match deterministic numbering rule")
        edges = 0
        for left in range(60):
            for right in range(left + 1, 60):
                distance = K()
                for axis in range(3):
                    difference = parsed[left][axis] - parsed[right][axis]
                    distance += difference * difference
                if distance == K(Fraction(4)):
                    edges += 1
        require(edges == 120, f"vertex table has {edges} RID edges, expected 120")
        return parsed

    @staticmethod
    def _validate_inequalities(data: Any) -> list[dict[str, Any]]:
        require(type(data) is dict and data.get("format") == "rid-cover-domain-inequalities/1",
                "domain table: invalid format")
        require(data.get("field") == "Q(sqrt5)", "domain table: invalid field")
        require(data.get("variable_order") == ["s", "t", "r1", "r2", "r3"],
                "domain table: invalid variable order")
        require(data.get("sign_convention") == "q_i <= 0", "domain table: invalid sign convention")
        rows = data.get("inequalities")
        require(type(rows) is list and len(rows) == 73, "domain table: expected 73 rows")
        polynomials: list[Poly] = []
        for index, row in enumerate(rows):
            require(type(row) is dict and row.get("index") == index, f"domain row {index}: wrong index")
            require(row.get("relation") == "<=0", f"domain row {index}: wrong relation")
            require(row.get("variables") == ["s", "t", "r1", "r2", "r3"],
                    f"domain row {index}: wrong variables")
            degree = row.get("homogeneous_view_degree")
            require(type(degree) is int and degree in (0, 1, 2), f"domain row {index}: invalid view degree")
            terms = row.get("terms")
            require(type(terms) is list and terms, f"domain row {index}: empty terms")
            polynomial: Poly = {}
            seen = set()
            for term_index, term in enumerate(terms):
                require(type(term) is dict and set(term) == {"coefficient", "exponents"},
                        f"domain row {index} term {term_index}: invalid fields")
                coefficient = parse_k(term["coefficient"], f"domain row {index} term {term_index}")
                require(not coefficient.is_zero(), f"domain row {index} term {term_index}: zero coefficient")
                exponents_json = exact_list(term["exponents"], 5,
                                            f"domain row {index} term {term_index}.exponents")
                require(all(type(item) is int and item >= 0 for item in exponents_json),
                        f"domain row {index} term {term_index}: invalid exponent")
                exponents = tuple(exponents_json)
                require(exponents not in seen, f"domain row {index}: repeated monomial")
                require(exponents[0] + exponents[1] <= degree,
                        f"domain row {index}: monomial exceeds homogeneous view degree")
                seen.add(exponents)
                polynomial[exponents] = coefficient
            polynomials.append(polynomial)

        phi = K(Fraction(1, 2), Fraction(1, 2))
        expected_q0 = {ZERO_EXP: K(Fraction(-1)), (1, 0, 0, 0, 0): phi,
                       (0, 1, 0, 0, 0): phi * phi}
        require(polynomials[0] == expected_q0, "domain row 0 does not match q0")
        signs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for index in range(1, 13):
            k = index - 1
            axis = k // 4
            first, second = signs[k % 4]
            expected = {ZERO_EXP: phi - 2}
            first_exp = [0] * 5
            first_exp[2 + axis] = 1
            second_exp = [0] * 5
            second_exp[2 + ((axis + 1) % 3)] = 1
            expected[tuple(first_exp)] = K(Fraction(first))
            expected[tuple(second_exp)] = (phi - 1) * second
            require(polynomials[index] == expected, f"domain row {index} does not match rotation rule")
        return rows

    @staticmethod
    def _validate_inventory(data: Any) -> dict[str, Any]:
        require(type(data) is dict and data.get("format") == "rid-cover-inventory/1",
                "cover inventory: invalid format")
        covers = data.get("covers")
        require(data.get("cover_count") == 38 and type(covers) is list and len(covers) == 38,
                "cover inventory: expected 38 covers")
        required_paths = {f"local/{index}.json" for index in range(30)}
        required_paths.update(f"exotic/{name}.json" for name in
                              ("square", "pentagon", "arc+", "arc-", "endpoint+", "endpoint-",
                               "crossing+", "crossing-"))
        seen_paths: set[str] = set()
        zoom_count = 0
        for cover_index, cover in enumerate(covers):
            require(type(cover) is dict and set(cover) == {
                "base_dimension", "name", "offset_dimension", "parameters", "path", "scope", "zooms"
            }, f"cover inventory entry {cover_index}: invalid fields")
            path = cover["path"]
            require(type(path) is str and path in required_paths and path not in seen_paths,
                    f"cover inventory entry {cover_index}: invalid or repeated path")
            seen_paths.add(path)
            if path.startswith("local/"):
                require(cover["name"] == path[6:-5] and cover["scope"] == "all",
                        f"cover inventory {path}: invalid local identity")
            else:
                require(cover["name"] == path[7:-5] and cover["scope"] == "domain",
                        f"cover inventory {path}: invalid exotic identity")
            validate_parameters(cover["parameters"], f"cover inventory {path}.parameters", False)
            shape_data = next(iter(cover["parameters"]["shape"].values()))
            require(cover["base_dimension"] == len(shape_data["base"]),
                    f"cover inventory {path}: wrong base dimension")
            require(cover["offset_dimension"] == len(shape_data["offset"]),
                    f"cover inventory {path}: wrong offset dimension")
            expected_zooms = derive_zooms(cover["parameters"])
            require(cover["zooms"] == expected_zooms,
                    f"cover inventory {path}: zoom inventory does not follow generation rules")
            for zoom_index, zoom in enumerate(expected_zooms):
                parse_root(zoom["root"], f"cover inventory {path}.zooms[{zoom_index}].root")
            zoom_count += len(expected_zooms)
        require(seen_paths == required_paths, "cover inventory: missing required cover")
        require(data.get("zoom_count") == 334 and zoom_count == 334,
                f"cover inventory: found {zoom_count} roots, expected 334")
        return data

    def is_edge(self, start: int, end: int) -> bool:
        if start == end:
            return False
        distance = K()
        for axis in range(3):
            difference = self.vertices[start][axis] - self.vertices[end][axis]
            distance += difference * difference
        return distance == K(Fraction(4))


def validate_witness(witness: Any, scope: str, specification: Specification, where: str) -> dict[str, Any]:
    require(type(witness) is dict, f"{where}: expected witness object")
    keys = list(witness)
    if keys == ["edge", "vertex"]:
        edge = exact_list(witness["edge"], 2, f"{where}.edge")
        start = exact_int(edge[0], 0, 59, f"{where}.edge[0]")
        end = exact_int(edge[1], 0, 59, f"{where}.edge[1]")
        exact_int(witness["vertex"], 0, 59, f"{where}.vertex")
        require(specification.is_edge(start, end), f"{where}.edge: unordered pair is not an RID edge")
    elif keys == ["direction", "contact", "vertex"]:
        direction = exact_list(witness["direction"], 2, f"{where}.direction")
        parsed = [parse_k(item, f"{where}.direction[{index}]") for index, item in enumerate(direction)]
        require(not all(item.is_zero() for item in parsed), f"{where}.direction: zero direction")
        exact_int(witness["contact"], 0, 59, f"{where}.contact")
        exact_int(witness["vertex"], 0, 59, f"{where}.vertex")
    elif keys == ["inequality"]:
        exact_int(witness["inequality"], 0, 72, f"{where}.inequality")
        require(scope == "domain", f"{where}: domain witness forbidden for scope all")
    else:
        raise CheckError(f"{where}: invalid witness fields or field order")
    return witness


def validate_leaf(value: Any, witness_count: int, distance_variables: list[int], where: str) -> str | tuple[int, tuple[int, ...]]:
    if value == "delegated" and type(value) is str:
        return "delegated"
    leaf = exact_keys(value, ["witness"], where)
    record = exact_keys(leaf["witness"], ["index", "factor"], f"{where}.witness")
    index = exact_int(record["index"], 0, witness_count - 1, f"{where}.witness.index")
    factor_json = exact_list(record["factor"], 5, f"{where}.witness.factor")
    factor = tuple(exact_int(value, 0, 255, f"{where}.witness.factor[{axis}]")
                   for axis, value in enumerate(factor_json))
    for axis, exponent in enumerate(factor):
        require(exponent == 0 or axis in distance_variables,
                f"{where}.witness.factor: positive exponent at non-distance variable {axis}")
    return index, factor


def validate_beyond(parameters: dict[str, Any], specification: Specification, where: str) -> None:
    beyond = parameters["beyond"]
    if beyond is None:
        return
    require(parameters["coordinates"] == "configuration",
            f"{where}: beyond requires configuration coordinates")
    z = [pvar(index) for index in range(5)]
    u, r = configuration_polynomials(parameters, z)
    q = domain_polynomial(specification.inequality_rows[beyond["inequality"]], u, r)
    axis = beyond["axis"]
    bounds = covered_bounds(parameters)
    require(len(bounds) == 5 and all(lo < hi for lo, hi in bounds),
            f"{where}: invalid remaining containment bounds")
    upper = bounds[axis][1]
    unit = [0] * 5
    unit[axis] = 1
    exponent = tuple(unit)
    kappa = q.get(exponent, K())
    require(kappa.sign() > 0, f"{where}: beyond coefficient kappa is not positive")
    expected = {exponent: kappa}
    constant = -kappa * upper
    if not constant.is_zero():
        expected[ZERO_EXP] = constant
    require(q == expected, f"{where}: beyond polynomial is not kappa*(z_axis-upper)")


def validate_delegated(parameters: dict[str, Any], inventory_zoom: dict[str, Any],
                       zoom_map: ZoomMap, cell: tuple[tuple[Fraction, Fraction], ...],
                       all_inventory_zooms: list[dict[str, Any]], where: str) -> None:
    require(inventory_zoom["family"] == "a", f"{where}: delegation requires unsheared family A")
    point = parameters["shape"].get("point")
    require(point is not None and point["window"] is not None,
            f"{where}: delegation requires a point window")
    window = point["window"]
    base_face = inventory_zoom["base_face"]
    require(base_face in window["faces"], f"{where}: source base face is outside window faces")
    assert zoom_map.base_unit is not None and zoom_map.rho is not None and zoom_map.mu is not None
    shear = [[parse_rational(item) for item in row] for row in window["shear"]]
    w: list[Poly] = []
    for row in range(len(point["offset"])):
        value = pmul(zoom_map.rho, zoom_map.offset_unit[row])
        for column in range(len(point["base"])):
            value = padd(value, pscale(zoom_map.base_unit[column], shear[row][column]))
        w.append(value)
        lo, hi = interval_range(value, cell, f"{where}.window[{row}]")
        radius = parse_rational(window["radius"])
        allowed_lo = K(Fraction(point["offset"][row][0]) * radius)
        allowed_hi = K(Fraction(point["offset"][row][1]) * radius)
        require((lo - allowed_lo).sign() >= 0 and (allowed_hi - hi).sign() >= 0,
                f"{where}: delegated window containment fails at offset axis {row}")

    expected_targets = face_list(point["offset"])
    targets = [zoom for zoom in all_inventory_zooms
               if zoom["family"] == "sheared-a" and zoom["base_face"] == base_face]
    require([target["offset_face"] for target in targets] == expected_targets,
            f"{where}: sheared target roots are incomplete or have extras")

    source_base = zoom_map.z[:len(point["base"])]
    source_offset = zoom_map.z[len(point["base"]):]
    reconstructed = []
    for row in range(len(source_offset)):
        value = pmul(zoom_map.mu, w[row])
        correction: Poly = {}
        for column in range(len(source_base)):
            correction = padd(correction, pscale(source_base[column], shear[row][column]))
        reconstructed.append(psub(value, correction))
    require(reconstructed == source_offset,
            f"{where}: source and sheared target adapted-coordinate maps differ")


def hole_vertex_for(witness: dict[str, Any], specification: Specification) -> list[K] | None:
    if "edge" in witness:
        return specification.vertices[witness["edge"][0]]
    if "direction" in witness:
        return specification.vertices[witness["contact"]]
    return None


def validate_cover(path: Path, expected_path: str, specification: Specification) -> dict[str, int]:
    document = strict_load(path)
    cover = exact_keys(document, ["format", "name", "scope", "parameters", "witnesses", "zooms"],
                       expected_path)
    require(cover["format"] == "rid-cover/1", f"{expected_path}: wrong format")
    require(type(cover["name"]) is str, f"{expected_path}.name: expected string")
    require(cover["scope"] in ("all", "domain"), f"{expected_path}.scope: invalid scope")
    validate_parameters(cover["parameters"], f"{expected_path}.parameters")
    inventory_cover = specification.cover_by_path.get(expected_path)
    require(inventory_cover is not None, f"{expected_path}: no required inventory entry")
    require(cover["name"] == inventory_cover["name"], f"{expected_path}: wrong cover name")
    require(cover["scope"] == inventory_cover["scope"], f"{expected_path}: wrong cover scope")
    require(cover["parameters"] == inventory_cover["parameters"], f"{expected_path}: parameters differ from inventory")
    validate_beyond(cover["parameters"], specification, f"{expected_path}.parameters.beyond")

    witnesses_json = exact_list(cover["witnesses"], None, f"{expected_path}.witnesses")
    witnesses = [validate_witness(value, cover["scope"], specification,
                                  f"{expected_path}.witnesses[{index}]")
                 for index, value in enumerate(witnesses_json)]
    zooms_json = exact_list(cover["zooms"], None, f"{expected_path}.zooms")
    inventory_zooms = inventory_cover["zooms"]
    require(len(zooms_json) == len(inventory_zooms),
            f"{expected_path}: zoom count differs from required roots")

    metrics = {"zooms": len(zooms_json), "leaves": 0, "witness_leaves": 0,
               "delegated_leaves": 0, "corner_evaluations": 0, "bernstein_coefficients": 0}
    polynomial_cache: dict[tuple[int, int], tuple[Poly, list[Poly] | None]] = {}
    quotient_cache: dict[tuple[int, int, tuple[int, ...]], Poly] = {}

    for zoom_index, (zoom_json, inventory_zoom) in enumerate(zip(zooms_json, inventory_zooms)):
        where = f"{expected_path}.zooms[{zoom_index}]"
        zoom = exact_keys(zoom_json, ["name", "tree", "leaves"], where)
        require(zoom["name"] == inventory_zoom["name"], f"{where}: wrong zoom name or order")
        root = parse_root(inventory_zoom["root"], f"inventory {expected_path}.zooms[{zoom_index}].root")
        cells = parse_tree(zoom["tree"], root, f"{where}.tree")
        leaves_json = exact_list(zoom["leaves"], None, f"{where}.leaves")
        require(len(leaves_json) == len(cells), f"{where}: tree/leaf count mismatch")
        metrics["leaves"] += len(cells)

        zoom_map = build_zoom_map(cover["parameters"], inventory_zoom)
        u, r = configuration_polynomials(cover["parameters"], zoom_map.z)
        for component_index, component in enumerate(u):
            require(all(all(exponent <= 1 for exponent in term) for term in component),
                    f"{where}: view component {component_index} is not multilinear")

        for leaf_index, (leaf_json, cell) in enumerate(zip(leaves_json, cells)):
            leaf_where = f"{where}.leaves[{leaf_index}]"
            leaf = validate_leaf(leaf_json, len(witnesses), inventory_zoom["distance_variables"], leaf_where)
            if leaf == "delegated":
                metrics["delegated_leaves"] += 1
                validate_delegated(cover["parameters"], inventory_zoom, zoom_map, cell,
                                   inventory_zooms, leaf_where)
                continue

            metrics["witness_leaves"] += 1
            witness_index, factor = leaf
            witness = witnesses[witness_index]
            cache_key = zoom_index, witness_index
            if cache_key not in polynomial_cache:
                polynomial_cache[cache_key] = witness_polynomial(witness, u, r, specification)
            polynomial, normal = polynomial_cache[cache_key]
            quotient_key = zoom_index, witness_index, factor
            if quotient_key not in quotient_cache:
                quotient_cache[quotient_key] = pdivide_monomial(polynomial, factor, leaf_where)
            quotient = quotient_cache[quotient_key]
            hole_vertex = hole_vertex_for(witness, specification)
            metrics["corner_evaluations"] += validate_corner_conditions(
                u, normal, hole_vertex, specification.vertices, cell, leaf_where)
            metrics["bernstein_coefficients"] += require_negative_bernstein(quotient, cell, leaf_where)
    return metrics


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_catalogue(output: Path | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    specification = Specification()
    expected_paths = set(specification.cover_by_path)
    actual_paths = set()
    for grouping in ("local", "exotic"):
        directory = INPUT_DIR / grouping
        actual_paths.update(f"{grouping}/{path.name}" for path in directory.glob("*.json"))
    require(actual_paths == expected_paths,
            f"input catalogue differs from required paths: missing={sorted(expected_paths-actual_paths)}, "
            f"extra={sorted(actual_paths-expected_paths)}")

    results = []
    for relative in sorted(expected_paths, key=lambda value: (value.split("/")[0], value)):
        path = INPUT_DIR / relative
        file_started = time.perf_counter()
        try:
            metrics = validate_cover(path, relative, specification)
            status = "pass"
            diagnostic = None
        except CheckError as error:
            metrics = None
            status = "fail"
            diagnostic = str(error)
        results.append({
            "path": relative,
            "sha256": sha256(path),
            "status": status,
            "diagnostic": diagnostic,
            "metrics": metrics,
            "runtime_seconds": round(time.perf_counter() - file_started, 6),
        })
    verdict = "pass" if all(result["status"] == "pass" for result in results) else "fail"
    manifest = {
        "format": "rid-cover-clean-room-result/1",
        "specification_version": "rid-cover/1-spec.1",
        "checker": "clean-room-v2",
        "arithmetic": "exact Q(sqrt(5))",
        "verdict": verdict,
        "cover_count": len(results),
        "results": results,
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if output is not None:
        output.write_bytes(encoded)
    else:
        sys.stdout.buffer.write(encoded)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="check the complete required catalogue")
    parser.add_argument("--output", type=Path, help="write the result manifest")
    parser.add_argument("path", nargs="?", type=Path, help="check one permitted cover file")
    arguments = parser.parse_args()
    try:
        if arguments.all:
            require(arguments.path is None, "do not combine --all with a path")
            manifest = run_catalogue(arguments.output)
            return 0 if manifest["verdict"] == "pass" else 1
        require(arguments.path is not None, "supply --all or one cover path")
        resolved = arguments.path.resolve()
        require(resolved.parent in ((INPUT_DIR / "local").resolve(), (INPUT_DIR / "exotic").resolve()),
                "single-file path is outside the permitted input directories")
        specification = Specification()
        relative = f"{resolved.parent.name}/{resolved.name}"
        metrics = validate_cover(resolved, relative, specification)
        print(json.dumps({"path": relative, "status": "pass", "metrics": metrics}, indent=2))
        return 0
    except CheckError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
