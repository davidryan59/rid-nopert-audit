"""Validation of explicit binary midpoint-subdivision trees."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from boxes import Box


class TreeValidationError(ValueError):
    pass


@dataclass(frozen=True)
class SubdivisionLeaf:
    identifier: str
    box: Box
    payload: Any = None


@dataclass(frozen=True)
class SubdivisionNode:
    axis: int
    box: Box
    lower: SubdivisionNode | SubdivisionLeaf | None
    upper: SubdivisionNode | SubdivisionLeaf | None


@dataclass(frozen=True)
class ValidatedLeaf:
    identifier: str
    box: Box
    payload: Any


def validate_subdivision_tree(
    root: SubdivisionNode | SubdivisionLeaf,
    expected_root: Box,
) -> list[ValidatedLeaf]:
    """Prove structural completeness against declared child boxes."""
    seen_objects: set[int] = set()
    seen_leaf_identifiers: set[str] = set()
    leaves: list[ValidatedLeaf] = []

    def visit(node: SubdivisionNode | SubdivisionLeaf | None, expected_box: Box) -> None:
        if node is None:
            raise TreeValidationError("subdivision node has a missing child")
        object_id = id(node)
        if object_id in seen_objects:
            raise TreeValidationError("tree reuses a node or contains a cycle")
        seen_objects.add(object_id)
        if node.box != expected_box:
            raise TreeValidationError("declared cell differs from its exact midpoint path")
        if isinstance(node, SubdivisionLeaf):
            if not isinstance(node.identifier, str) or not node.identifier:
                raise TreeValidationError("leaf identifier must be a nonempty string")
            if node.identifier in seen_leaf_identifiers:
                raise TreeValidationError("duplicate leaf identifier")
            seen_leaf_identifiers.add(node.identifier)
            leaves.append(ValidatedLeaf(node.identifier, node.box, node.payload))
            return
        if not isinstance(node, SubdivisionNode):
            raise TreeValidationError("unknown tree node type")
        if not isinstance(node.axis, int) or node.axis < 0 or node.axis >= expected_box.dimension:
            raise TreeValidationError("split axis lies outside the root dimension")
        expected_lower, expected_upper = expected_box.split(node.axis)
        visit(node.lower, expected_lower)
        visit(node.upper, expected_upper)

    visit(root, expected_root)
    return leaves
