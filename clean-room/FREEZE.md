# Clean-room freeze

## Summary

The strict clean-room checker was frozen on 2026-10-08 before any prohibited source or prior audit material was inspected.
Its result is **inconclusive**.
The public article defines the mathematics, but it does not define eleven serialization conventions needed to interpret `rid-cover/1`.

## Freeze record

- **Freeze time:** 2026-10-08T12:23:19Z
- **Audited upstream commit:** `802a3ded09535c4a99cef1371ce0d0277c433fa8`
- **Audit repository HEAD:** `0bee35fc00c875988e38f0f35d464b329f6e5edf`
- **Working-tree state:** the complete `clean-room/` directory was untracked; no clean-room file was staged
- **Source-tree SHA-256:** `f2843d2d93bd076a638775aabd6c00f5d675f668ed2a6ca65ffe4ac1796be6e5`
- **Source-hash method:** SHA-256 of `results/source-hashes-pre-comparison.sha256`, whose sorted scope is the three source documents, dependency statement, runner, `src/*.py`, and `tests/*.py`
- **Input hashes:** all 39 SHA-256 values are stored in `results/clean-room-result.json`
- **Dependencies:** Python 3.8.13 standard library only; no third-party packages
- **Reproduction command:** `/Users/davidryan/code/projects/rid-nopert-audit/clean-room/run.sh`

## Pre-comparison result

The complete run passed 55 of 55 unit and mutation tests.
The checker returned `inconclusive` with eleven public-specification blockers.
The checker runtime was 0.116214958 seconds within a one-second complete run.

The input inventory contained:

- 38 cover files;
- 334 root zoom records;
- 11,231 stored leaf records;
- 11,183 stored witness leaf records;
- 48 stored delegated leaf records;
- 716 witness definitions.

These values are syntactic inventory counts.
They are not validated mathematical cell counts.
The checker reconstructed zero serialized cells, so `mathematically_checked_cells` is zero.

The machine-readable result records every cover, its stored counts, each blocked obligation, all input hashes, dependencies, runtime, failures, and warnings.
The captured test and checker output is in `results/run.log`.

## Exact blocker

The article and copied JSON files do not define:

1. the vertex index order;
2. the domain-inequality index order;
3. the tree-string grammar and leaf association;
4. the zoom-name grammar;
5. the zoom coordinate and factor order;
6. the affine-map orientation and adapted-coordinate composition;
7. the witness object field semantics;
8. the face-radius order;
9. the delegated hand-over binding;
10. the pentagon extension index encoding;
11. the complete `rid-cover/1` schema and rejection rules.

These omissions block cell reconstruction, witness reconstruction, exact division, support checks, Bernstein signs, completeness, hand-overs, and the pentagon binding.
The checker refuses to infer these rules from programming conventions or expected output.

## Prior knowledge

The Maths Search front door disclosed these aggregate results before implementation:

- the proof has 38 zoom covers;
- the repository's second Rust model accepted 11,183 zoom cells;
- the Rust and Python checkers accepted 192,696 records;
- the existing audit reported overall confirmation subject to its assumptions.

The implementation was therefore source-isolated but not result-blinded.
The known aggregates were recorded before development and were not used to tune, repair, or terminate the checker.

## Boundary at freeze

Before this file existed, the session did not read or execute the existing audit document, audit report, manifest, logs, upstream implementation, upstream tests, validation data, figures, audit code, or build script.
It used only the repository rules, the project front door, the pinned article, and the 38 permitted JSON inputs.

The pre-comparison source manifest, result, and run log preserve this state.
Any later proof-algorithm change requires a new dated freeze entry with its reason and a new source-tree hash.

## Post-freeze documentation correction

At 2026-10-08T12:40:14Z, the README test total was corrected from 54 to 55.
The final pre-freeze run had already reported 55 tests after the support-control repair.
No proof algorithm, test, input, machine result or comparison result changed.

- **Preserved pre-comparison source hash:** `f2843d2d93bd076a638775aabd6c00f5d675f668ed2a6ca65ffe4ac1796be6e5`
- **Preserved manifest:** `results/source-hashes-pre-comparison.sha256`
- **Current documentation-corrected source hash:** `9e89abf09a99eeccd5250e6cd87f5b894429e6dfce1003d2c45b228b9c579686`
- **Current manifest:** `results/source-hashes.sha256`

The original freeze entry and run log remain unchanged.
