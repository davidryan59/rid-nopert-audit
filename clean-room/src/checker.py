#!/usr/bin/env python3
"""Strict clean-room front end.

The checker fails closed with an inconclusive result because the permitted
public material does not define the rid-cover/1 witness and tree encoding.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from exact import Q5
from geometry import PHI, PHI_BAR, verify_arc_plane_support_equality
from polynomial import Polynomial
from public_parameters import validate_public_parameters
from schema import InputValidationError, validate_input_directory


BLOCKERS = [
    {
        "id": "vertex-numbering",
        "fields": ["witnesses[].vertex", "witnesses[].contact", "witnesses[].edge"],
        "missing_definition": "Equation (2.1) defines an unordered set and supplies no JSON vertex index order.",
        "blocked_obligations": ["witness reconstruction", "support conditions", "Bernstein sign"],
    },
    {
        "id": "domain-inequality-numbering",
        "fields": ["witnesses[].inequality", "parameters.beyond.inequality"],
        "missing_definition": "The article gives inequality families but no serialized index-to-polynomial table.",
        "blocked_obligations": ["domain witness reconstruction", "pentagon extension binding"],
    },
    {
        "id": "tree-grammar",
        "fields": ["zooms[].tree", "zooms[].leaves"],
        "missing_definition": "The digit-and-dot grammar, traversal, child order, and leaf-array association are unstated.",
        "blocked_obligations": ["cell reconstruction", "prefix freedom", "root coverage completeness"],
    },
    {
        "id": "zoom-name-grammar",
        "fields": ["zooms[].name"],
        "missing_definition": "The names do not normatively bind records to root families, axes, or signed faces.",
        "blocked_obligations": ["root reconstruction", "zero-set implication"],
    },
    {
        "id": "zoom-coordinate-order",
        "fields": ["zooms[].tree", "zooms[].leaves[].witness.factor"],
        "missing_definition": "The article does not bind split digits or factor positions to the five zoom coordinates.",
        "blocked_obligations": ["distance nonnegativity", "zero-set implication", "exact monomial division"],
    },
    {
        "id": "affine-map-semantics",
        "fields": ["parameters.coordinates", "parameters.centre", "parameters.map"],
        "missing_definition": "The JSON matrix orientation and its composition with adapted coordinates are unstated.",
        "blocked_obligations": ["cell coordinate map", "pulled-back witness", "map containment"],
    },
    {
        "id": "witness-object-semantics",
        "fields": ["witnesses[].edge", "witnesses[].direction", "witnesses[].contact"],
        "missing_definition": "The article does not bind these JSON alternatives to the gap-witness formulas.",
        "blocked_obligations": ["witness reconstruction", "support conditions"],
    },
    {
        "id": "face-radius-order",
        "fields": ["parameters.shape.point.radii"],
        "missing_definition": "Face-dependent radius entries are not bound to an ordered list of signed faces.",
        "blocked_obligations": ["root reconstruction"],
    },
    {
        "id": "delegation-binding",
        "fields": ["zooms[].leaves[] == delegated", "parameters.shape.point.window"],
        "missing_definition": "A delegated leaf names no target and no public rule selects its sheared target.",
        "blocked_obligations": ["hand-over containment", "delegated coverage"],
    },
    {
        "id": "pentagon-extension-encoding",
        "fields": ["parameters.beyond.axis", "parameters.beyond.inequality"],
        "missing_definition": "The article proves the extension but does not define these serialized indices.",
        "blocked_obligations": ["pentagon extension binding"],
    },
    {
        "id": "rid-cover-schema",
        "fields": ["format == rid-cover/1"],
        "missing_definition": "No public schema defines all types, enumerations, rejection rules, and unknown-field handling.",
        "blocked_obligations": ["authoritative proof-data parsing"],
    },
]


def pentagon_identity_is_exact() -> bool:
    s = Polynomial.variable(2, 0)
    t = Polynomial.variable(2, 1)
    xi = s + t * PHI + PHI_BAR
    difference = xi * PHI - (s * PHI + t * (PHI**2) - 1)
    return difference.is_zero()


def run(inputs: Path) -> dict:
    started = time.perf_counter()
    inventories, input_hashes = validate_input_directory(inputs)
    validate_public_parameters(inputs)
    arc_support = verify_arc_plane_support_equality()
    if not pentagon_identity_is_exact():
        raise ArithmeticError("pentagon domain identity failed")

    covers = []
    for inventory in inventories:
        covers.append(
            {
                "name": inventory.name,
                "input": inventory.relative_path,
                "root_zoom_records": inventory.zoom_count,
                "stored_leaf_records": inventory.stored_leaf_count,
                "stored_witness_leaves": inventory.stored_witness_leaf_count,
                "stored_delegated_leaves": inventory.stored_delegated_leaf_count,
                "witness_definitions": inventory.witness_definition_count,
                "status": "not_mathematically_checked",
                "obligations": {
                    "distance_nonnegative": "blocked",
                    "zero_set_maps_to_no_fit": "blocked",
                    "exact_division": "blocked",
                    "support_corners": "blocked",
                    "strict_bernstein_sign": "blocked",
                    "subdivision_completeness": "blocked",
                    "hand_over": "blocked" if inventory.name.startswith("crossing") else "not_applicable",
                    "pentagon_extension": "blocked" if inventory.name == "pentagon" else "not_applicable",
                },
            }
        )

    elapsed = time.perf_counter() - started
    return {
        "format": "rid-clean-room-result/1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audited_upstream_commit": "802a3ded09535c4a99cef1371ce0d0277c433fa8",
        "result": "inconclusive",
        "strict_clean_room": True,
        "source_isolated": True,
        "result_blinded": False,
        "reason": "The article and declarative inputs do not define the rid-cover/1 semantics needed to reconstruct cells and witnesses.",
        "independent_checks_completed": {
            "exact_input_inventory": "passed",
            "fail_closed_syntactic_validation": "passed",
            "article_parameter_consistency": "passed",
            "arc_plane_no_fit_support_equality": {
                key: value.to_json() for key, value in arc_support.items()
            },
            "pentagon_domain_identity": "passed",
        },
        "input_hashes_sha256": input_hashes,
        "cover_count": len(covers),
        "covers": covers,
        "derived_counts": {
            "root_zoom_records": sum(cover["root_zoom_records"] for cover in covers),
            "stored_leaf_records": sum(cover["stored_leaf_records"] for cover in covers),
            "stored_witness_leaves": sum(cover["stored_witness_leaves"] for cover in covers),
            "stored_delegated_leaves": sum(cover["stored_delegated_leaves"] for cover in covers),
            "witness_definitions": sum(cover["witness_definitions"] for cover in covers),
        },
        "mathematically_checked_cells": 0,
        "blockers": BLOCKERS,
        "warnings": [
            "Stored record counts are inventory facts, not validated cell counts.",
            "No tree string, witness index, factor position, or delegated marker was assigned guessed semantics.",
        ],
        "dependencies": {
            "third_party": [],
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "runtime_seconds": elapsed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, default=Path("inputs"))
    parser.add_argument("--output", type=Path, default=Path("results/clean-room-result.json"))
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="return status 2 unless every proof obligation passed",
    )
    arguments = parser.parse_args()
    try:
        result = run(arguments.inputs)
        exit_code = 2 if arguments.require_pass else 0
    except (InputValidationError, ArithmeticError, OSError, ValueError) as error:
        result = {
            "format": "rid-clean-room-result/1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "audited_upstream_commit": "802a3ded09535c4a99cef1371ce0d0277c433fa8",
            "result": "invalid_input",
            "error": str(error),
        }
        exit_code = 1
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with arguments.output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"clean-room result: {result['result']}")
    if "derived_counts" in result:
        counts = result["derived_counts"]
        print(
            "derived inventory: "
            f"{result['cover_count']} covers, "
            f"{counts['stored_witness_leaves']} witness leaves, "
            f"{counts['stored_delegated_leaves']} delegated leaves"
        )
    if result["result"] == "inconclusive":
        print(f"blocking public-specification omissions: {len(result['blockers'])}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
