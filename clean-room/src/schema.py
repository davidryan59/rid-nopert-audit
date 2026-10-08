"""Fail-closed syntactic validation of the copied declarative inputs.

The public article does not define the semantics of rid-cover/1.  This module
therefore validates only properties that do not require guessing those
semantics.  A successful return is not a mathematical cover result.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from exact import Q5, parse_fraction


EXPECTED_LOCAL = tuple(f"local/{index}.json" for index in range(30))
EXPECTED_EXOTIC = (
    "exotic/arc+.json",
    "exotic/arc-.json",
    "exotic/endpoint+.json",
    "exotic/endpoint-.json",
    "exotic/crossing+.json",
    "exotic/crossing-.json",
    "exotic/pentagon.json",
    "exotic/square.json",
)
EXPECTED_JSON = EXPECTED_LOCAL + EXPECTED_EXOTIC
EXPECTED_INPUTS = ("article.pdf",) + EXPECTED_JSON


class InputValidationError(ValueError):
    pass


@dataclass(frozen=True)
class CoverInventory:
    relative_path: str
    name: str
    zoom_count: int
    stored_leaf_count: int
    stored_witness_leaf_count: int
    stored_delegated_leaf_count: int
    witness_definition_count: int


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_input_directory(root: Path) -> tuple[list[CoverInventory], dict[str, str]]:
    root = root.resolve()
    if not root.is_dir():
        raise InputValidationError(f"input directory does not exist: {root}")
    actual = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    )
    expected = sorted(EXPECTED_INPUTS)
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise InputValidationError(f"input inventory mismatch; missing={missing}, extra={extra}")

    article = root / "article.pdf"
    with article.open("rb") as handle:
        if handle.read(5) != b"%PDF-":
            raise InputValidationError("article.pdf lacks a PDF header")

    inventories: list[CoverInventory] = []
    hashes = {"article.pdf": sha256_file(article)}
    for relative in EXPECTED_JSON:
        path = root / relative
        hashes[relative] = sha256_file(path)
        inventories.append(validate_cover_file(path, relative))
    return inventories, hashes


def validate_cover_file(path: Path, relative_path: str) -> CoverInventory:
    try:
        with path.open("r", encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise InputValidationError(f"{relative_path}: invalid JSON: {error}") from error
    _require_object(document, relative_path)
    _exact_keys(
        document,
        {"format", "name", "scope", "parameters", "witnesses", "zooms"},
        relative_path,
    )
    if document["format"] != "rid-cover/1":
        raise InputValidationError(f"{relative_path}: unsupported format")
    expected_name = Path(relative_path).stem
    if document["name"] != expected_name:
        raise InputValidationError(
            f"{relative_path}: cover name {document['name']!r} differs from {expected_name!r}"
        )
    if document["scope"] not in {"all", "domain"}:
        raise InputValidationError(f"{relative_path}: invalid scope")

    has_window = _validate_parameters(document["parameters"], f"{relative_path}.parameters")
    witnesses = document["witnesses"]
    if not isinstance(witnesses, list) or not witnesses:
        raise InputValidationError(f"{relative_path}.witnesses: expected a nonempty array")
    for index, witness in enumerate(witnesses):
        _validate_witness(witness, f"{relative_path}.witnesses[{index}]")

    zooms = document["zooms"]
    if not isinstance(zooms, list) or not zooms:
        raise InputValidationError(f"{relative_path}.zooms: expected a nonempty array")
    zoom_names: set[str] = set()
    leaf_count = 0
    witness_leaf_count = 0
    delegated_leaf_count = 0
    for zoom_index, zoom in enumerate(zooms):
        context = f"{relative_path}.zooms[{zoom_index}]"
        _require_object(zoom, context)
        _exact_keys(zoom, {"name", "tree", "leaves"}, context)
        if not isinstance(zoom["name"], str) or not zoom["name"]:
            raise InputValidationError(f"{context}.name: expected a nonempty string")
        if zoom["name"] in zoom_names:
            raise InputValidationError(f"{context}.name: duplicate zoom name")
        zoom_names.add(zoom["name"])
        if not isinstance(zoom["tree"], str) or not zoom["tree"]:
            raise InputValidationError(f"{context}.tree: expected a nonempty opaque string")
        leaves = zoom["leaves"]
        if not isinstance(leaves, list) or not leaves:
            raise InputValidationError(f"{context}.leaves: expected a nonempty array")
        leaf_count += len(leaves)
        for leaf_index, leaf in enumerate(leaves):
            leaf_context = f"{context}.leaves[{leaf_index}]"
            if leaf == "delegated":
                if not has_window:
                    raise InputValidationError(f"{leaf_context}: delegation without a hand-over window")
                delegated_leaf_count += 1
                continue
            _require_object(leaf, leaf_context)
            _exact_keys(leaf, {"witness"}, leaf_context)
            reference = leaf["witness"]
            _require_object(reference, f"{leaf_context}.witness")
            _exact_keys(reference, {"index", "factor"}, f"{leaf_context}.witness")
            witness_index = reference["index"]
            if (
                isinstance(witness_index, bool)
                or not isinstance(witness_index, int)
                or witness_index < 0
                or witness_index >= len(witnesses)
            ):
                raise InputValidationError(f"{leaf_context}.witness.index: invalid reference")
            factor = reference["factor"]
            if (
                not isinstance(factor, list)
                or len(factor) != 5
                or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in factor)
            ):
                raise InputValidationError(
                    f"{leaf_context}.witness.factor: expected five nonnegative integers"
                )
            witness_leaf_count += 1

    return CoverInventory(
        relative_path=relative_path,
        name=document["name"],
        zoom_count=len(zooms),
        stored_leaf_count=leaf_count,
        stored_witness_leaf_count=witness_leaf_count,
        stored_delegated_leaf_count=delegated_leaf_count,
        witness_definition_count=len(witnesses),
    )


def _validate_parameters(value: Any, context: str) -> bool:
    _require_object(value, context)
    _exact_keys(value, {"coordinates", "centre", "map", "shape", "beyond"}, context)
    coordinates = value["coordinates"]
    if coordinates != "configuration":
        _require_object(coordinates, f"{context}.coordinates")
        _exact_keys(coordinates, {"arc-plane"}, f"{context}.coordinates")
        if coordinates["arc-plane"] not in {"plus", "minus"}:
            raise InputValidationError(f"{context}.coordinates.arc-plane: invalid sign")

    centre = value["centre"]
    if not isinstance(centre, list) or len(centre) != 5:
        raise InputValidationError(f"{context}.centre: expected five field elements")
    for index, coefficient in enumerate(centre):
        _validate_q5(coefficient, f"{context}.centre[{index}]")

    matrix = value["map"]
    if not isinstance(matrix, list) or len(matrix) != 5:
        raise InputValidationError(f"{context}.map: expected five rows")
    for row_index, row in enumerate(matrix):
        if not isinstance(row, list) or len(row) != 5:
            raise InputValidationError(f"{context}.map[{row_index}]: expected five entries")
        for column_index, coefficient in enumerate(row):
            _validate_q5(coefficient, f"{context}.map[{row_index}][{column_index}]")

    shape = value["shape"]
    _require_object(shape, f"{context}.shape")
    if set(shape) == {"tube"}:
        _validate_tube(shape["tube"], f"{context}.shape.tube")
        has_window = False
    elif set(shape) == {"point"}:
        has_window = _validate_point(shape["point"], f"{context}.shape.point")
    else:
        raise InputValidationError(f"{context}.shape: expected exactly one tube or point definition")

    beyond = value["beyond"]
    if beyond is not None:
        _require_object(beyond, f"{context}.beyond")
        _exact_keys(beyond, {"axis", "inequality"}, f"{context}.beyond")
        _bounded_integer(beyond["axis"], 0, 4, f"{context}.beyond.axis")
        _bounded_integer(beyond["inequality"], 0, 72, f"{context}.beyond.inequality")
    return has_window


def _validate_tube(value: Any, context: str) -> None:
    _require_object(value, context)
    _exact_keys(value, {"base", "offset", "radius"}, context)
    _validate_box(value["base"], f"{context}.base")
    _validate_sign_box(value["offset"], f"{context}.offset")
    _positive_rational(value["radius"], f"{context}.radius")


def _validate_point(value: Any, context: str) -> bool:
    _require_object(value, context)
    _exact_keys(value, {"base", "offset", "radii", "radius", "ratio", "window"}, context)
    _validate_sign_box(value["base"], f"{context}.base")
    _validate_sign_box(value["offset"], f"{context}.offset")
    radii = value["radii"]
    if not isinstance(radii, list) or not radii:
        raise InputValidationError(f"{context}.radii: expected a nonempty array")
    for index, radius in enumerate(radii):
        _positive_rational(radius, f"{context}.radii[{index}]")
    _positive_rational(value["radius"], f"{context}.radius")
    _positive_rational(value["ratio"], f"{context}.ratio")
    window = value["window"]
    if window is None:
        return False
    _require_object(window, f"{context}.window")
    _exact_keys(window, {"faces", "shear", "radius"}, f"{context}.window")
    faces = window["faces"]
    if not isinstance(faces, list) or not faces:
        raise InputValidationError(f"{context}.window.faces: expected a nonempty array")
    for index, face in enumerate(faces):
        face_context = f"{context}.window.faces[{index}]"
        _require_object(face, face_context)
        _exact_keys(face, {"axis", "side"}, face_context)
        if isinstance(face["axis"], bool) or not isinstance(face["axis"], int) or face["axis"] < 0:
            raise InputValidationError(f"{face_context}.axis: invalid axis")
        if face["side"] not in {-1, 1}:
            raise InputValidationError(f"{face_context}.side: expected -1 or 1")
    shear = window["shear"]
    if not isinstance(shear, list) or not shear:
        raise InputValidationError(f"{context}.window.shear: expected a nonempty vector")
    for index, entry in enumerate(shear):
        if not isinstance(entry, list) or len(entry) != 1:
            raise InputValidationError(f"{context}.window.shear[{index}]: expected a singleton")
        parse_fraction(entry[0])
    _positive_rational(window["radius"], f"{context}.window.radius")
    return True


def _validate_witness(value: Any, context: str) -> None:
    _require_object(value, context)
    keys = set(value)
    if keys == {"edge", "vertex"}:
        edge = value["edge"]
        if not isinstance(edge, list) or len(edge) != 2:
            raise InputValidationError(f"{context}.edge: expected two vertex references")
        for index, vertex in enumerate(edge):
            _bounded_integer(vertex, 0, 59, f"{context}.edge[{index}]")
        if edge[0] == edge[1]:
            raise InputValidationError(f"{context}.edge: endpoints must differ")
        _bounded_integer(value["vertex"], 0, 59, f"{context}.vertex")
        return
    if keys == {"direction", "contact", "vertex"}:
        direction = value["direction"]
        if not isinstance(direction, list) or len(direction) != 2:
            raise InputValidationError(f"{context}.direction: expected two field elements")
        for index, coefficient in enumerate(direction):
            _validate_q5(coefficient, f"{context}.direction[{index}]")
        _bounded_integer(value["contact"], 0, 59, f"{context}.contact")
        _bounded_integer(value["vertex"], 0, 59, f"{context}.vertex")
        return
    if keys == {"inequality"}:
        _bounded_integer(value["inequality"], 0, 72, f"{context}.inequality")
        return
    raise InputValidationError(f"{context}: unknown witness fields {sorted(keys)}")


def _validate_box(value: Any, context: str) -> None:
    if not isinstance(value, list) or not value:
        raise InputValidationError(f"{context}: expected a nonempty box")
    for index, interval in enumerate(value):
        if not isinstance(interval, list) or len(interval) != 2:
            raise InputValidationError(f"{context}[{index}]: expected two endpoints")
        lower = parse_fraction(interval[0])
        upper = parse_fraction(interval[1])
        if lower > upper:
            raise InputValidationError(f"{context}[{index}]: reversed interval")


def _validate_sign_box(value: Any, context: str) -> None:
    _validate_box(value, context)
    for index, interval in enumerate(value):
        endpoints = (parse_fraction(interval[0]), parse_fraction(interval[1]))
        if endpoints not in {
            (Fraction(-1), Fraction(0)),
            (Fraction(0), Fraction(1)),
            (Fraction(-1), Fraction(1)),
        }:
            raise InputValidationError(f"{context}[{index}]: not a permitted sign interval")


def _validate_q5(value: Any, context: str) -> None:
    try:
        Q5.from_json(value)
    except ValueError as error:
        raise InputValidationError(f"{context}: {error}") from error


def _positive_rational(value: Any, context: str) -> None:
    try:
        parsed = parse_fraction(value)
    except ValueError as error:
        raise InputValidationError(f"{context}: {error}") from error
    if parsed <= 0:
        raise InputValidationError(f"{context}: expected a positive rational")


def _bounded_integer(value: Any, lower: int, upper: int, context: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
        raise InputValidationError(f"{context}: expected an integer in [{lower}, {upper}]")


def _require_object(value: Any, context: str) -> None:
    if not isinstance(value, dict):
        raise InputValidationError(f"{context}: expected an object")


def _exact_keys(value: dict[str, Any], expected: set[str], context: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise InputValidationError(f"{context}: missing fields {missing}; unknown fields {unknown}")
