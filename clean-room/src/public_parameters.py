"""Checks for cover parameters stated explicitly in Article Appendix B."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

from exact import parse_fraction
from schema import EXPECTED_JSON, InputValidationError


LOCAL_ROWS = (
    ("1/12", "1/6", "0", "1/10", "1/96"),
    ("0", "1/6", "1/10", "1/5", "1/80"),
    ("1/6", "1/3", "0", "1/10", "1/50"),
    ("1/6", "1/4", "1/10", "1/5", "1/50"),
    ("1/4", "1/3", "1/10", "3/20", "1/50"),
    ("1/4", "1/3", "3/20", "1/5", "1/50"),
    ("0", "1/12", "1/5", "3/10", "1/50"),
    ("1/12", "1/8", "1/5", "9/40", "1/50"),
    ("1/12", "1/8", "9/40", "1/4", "1/50"),
    ("1/8", "1/6", "1/5", "1/4", "1/200"),
    ("1/12", "1/8", "1/4", "3/10", "1/50"),
    ("1/8", "7/48", "1/4", "11/40", "1/50"),
    ("7/48", "1/6", "1/4", "21/80", "1/200"),
    ("7/48", "5/32", "21/80", "11/40", "1/50"),
    ("5/32", "31/192", "21/80", "43/160", "1/200"),
    ("1/8", "1/6", "11/40", "3/10", "1/50"),
    ("0", "1/6", "3/10", "2/5", "1/50"),
    ("1/6", "5/24", "1/5", "9/40", "1/50"),
    ("1/6", "3/16", "9/40", "1/4", "1/200"),
    ("3/16", "5/24", "9/40", "1/4", "1/50"),
    ("5/24", "1/4", "1/5", "9/40", "1/50"),
    ("5/24", "1/4", "9/40", "1/4", "1/200"),
    ("1/6", "3/16", "1/4", "21/80", "1/200"),
    ("3/16", "5/24", "1/4", "21/80", "1/200"),
    ("5/24", "11/48", "1/4", "11/40", "1/200"),
    ("1/4", "1/3", "1/5", "1/4", "1/50"),
    ("1/3", "1/2", "0", "1/10", "1/50"),
    ("1/3", "1/2", "1/10", "1/5", "1/50"),
    ("1/2", "7/12", "0", "1/10", "1/50"),
    ("7/12", "5/8", "0", "1/20", "1/20"),
)


def validate_public_parameters(inputs: Path) -> None:
    for index, row in enumerate(LOCAL_ROWS):
        document = _read(inputs / "local" / f"{index}.json")
        tube = document["parameters"]["shape"]["tube"]
        s0, s1, t0, t1, radius = map(parse_fraction, row)
        margin = Fraction(1, 1024)
        expected_base = (
            (max(Fraction(0), s0 - margin), min(Fraction(2, 3), s1 + margin)),
            (max(Fraction(0), t0 - margin), min(Fraction(2, 5), t1 + margin)),
        )
        _equal_box(tube["base"], expected_base, f"local/{index}.json base")
        _equal_sign_box(tube["offset"], ((-1, 1), (-1, 1), (-1, 1)), f"local/{index}.json offset")
        _equal_rational(tube["radius"], radius, f"local/{index}.json radius")
        if len(document["zooms"]) != 6:
            raise InputValidationError(f"local/{index}.json: Appendix B requires six root zooms")

    _validate_square(_read(inputs / "exotic" / "square.json"))
    _validate_pentagon(_read(inputs / "exotic" / "pentagon.json"))
    for sign in ("+", "-"):
        _validate_arc(_read(inputs / "exotic" / f"arc{sign}.json"), sign)
        _validate_endpoint(_read(inputs / "exotic" / f"endpoint{sign}.json"), sign)
        _validate_crossing(_read(inputs / "exotic" / f"crossing{sign}.json"), sign)


def _validate_square(document: dict[str, Any]) -> None:
    point = document["parameters"]["shape"]["point"]
    _equal_sign_box(point["base"], ((0, 1), (0, 1)), "square base")
    _equal_sign_box(point["offset"], ((-1, 1),) * 3, "square offset")
    _equal_rationals(point["radii"], (Fraction(1, 8), Fraction(1, 8)), "square base radii")
    _equal_rational(point["radius"], Fraction(1, 8), "square offset radius")
    _equal_rational(point["ratio"], Fraction(1), "square ratio")
    _require_zoom_count(document, 18)


def _validate_pentagon(document: dict[str, Any]) -> None:
    point = document["parameters"]["shape"]["point"]
    _equal_sign_box(point["base"], ((-1, 1), (-1, 0)), "pentagon base")
    _equal_sign_box(point["offset"], ((-1, 1),) * 3, "pentagon offset")
    _equal_rationals(point["radii"], (Fraction(1, 32),) * 3, "pentagon base radii")
    _equal_rational(point["radius"], Fraction(1, 16), "pentagon offset radius")
    _equal_rational(point["ratio"], Fraction(2), "pentagon ratio")
    if document["parameters"]["beyond"] != {"axis": 1, "inequality": 0}:
        raise InputValidationError("pentagon: extension descriptor differs from the copied article parameters")
    _require_zoom_count(document, 24)


def _validate_arc(document: dict[str, Any], sign: str) -> None:
    tube = document["parameters"]["shape"]["tube"]
    _equal_box(tube["base"], ((Fraction(3, 64), Fraction(3, 16)),), f"arc{sign} base")
    _equal_sign_box(tube["offset"], ((0, 1), (-1, 1), (-1, 1), (-1, 1)), f"arc{sign} offset")
    _equal_rational(tube["radius"], Fraction(1, 32), f"arc{sign} radius")
    _require_zoom_count(document, 7)


def _validate_endpoint(document: dict[str, Any], sign: str) -> None:
    point = document["parameters"]["shape"]["point"]
    _equal_sign_box(point["base"], ((-1, 1),), f"endpoint{sign} base")
    _equal_sign_box(
        point["offset"],
        ((0, 1), (-1, 1), (-1, 1), (-1, 1)),
        f"endpoint{sign} offset",
    )
    _equal_rationals(
        point["radii"],
        (Fraction(1, 16), Fraction(1, 32)),
        f"endpoint{sign} base radii",
    )
    _equal_rational(point["radius"], Fraction(1, 32), f"endpoint{sign} offset radius")
    _equal_rational(point["ratio"], Fraction(1), f"endpoint{sign} ratio")
    _require_zoom_count(document, 21)


def _validate_crossing(document: dict[str, Any], sign: str) -> None:
    point = document["parameters"]["shape"]["point"]
    _equal_sign_box(point["base"], ((-1, 1),), f"crossing{sign} base")
    _equal_sign_box(
        point["offset"],
        ((0, 1), (-1, 1), (-1, 1), (-1, 1)),
        f"crossing{sign} offset",
    )
    _equal_rationals(point["radii"], (Fraction(1, 16), Fraction(1, 16)), f"crossing{sign} base radii")
    _equal_rational(point["radius"], Fraction(1, 16), f"crossing{sign} offset radius")
    _equal_rational(point["ratio"], Fraction(5, 4), f"crossing{sign} ratio")
    window = point["window"]
    _equal_rational(window["radius"], Fraction(1, 4), f"crossing{sign} hand-over radius")
    if window["faces"] != [{"axis": 0, "side": 1}]:
        raise InputValidationError(f"crossing{sign}: hand-over must use the positive base face")
    shear = tuple(parse_fraction(entry[0]) for entry in window["shear"])
    if shear != (Fraction(0), Fraction(1), Fraction(0), Fraction(0)):
        raise InputValidationError(f"crossing{sign}: unexpected hand-over shear")
    _require_zoom_count(document, 28)


def _read(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _equal_box(value: Any, expected: Sequence[tuple[Fraction, Fraction]], context: str) -> None:
    parsed = tuple((parse_fraction(interval[0]), parse_fraction(interval[1])) for interval in value)
    if parsed != tuple(expected):
        raise InputValidationError(f"{context}: differs from Article Appendix B")


def _equal_sign_box(value: Any, expected: Sequence[tuple[int, int]], context: str) -> None:
    _equal_box(value, tuple((Fraction(a), Fraction(b)) for a, b in expected), context)


def _equal_rational(value: Any, expected: Fraction, context: str) -> None:
    if parse_fraction(value) != expected:
        raise InputValidationError(f"{context}: differs from the article")


def _equal_rationals(value: Any, expected: Sequence[Fraction], context: str) -> None:
    parsed = tuple(parse_fraction(entry) for entry in value)
    if parsed != tuple(expected):
        raise InputValidationError(f"{context}: differs from the article")


def _require_zoom_count(document: dict[str, Any], expected: int) -> None:
    if len(document["zooms"]) != expected:
        raise InputValidationError(
            f"{document['name']}: article requires {expected} root zooms, found {len(document['zooms'])}"
        )
