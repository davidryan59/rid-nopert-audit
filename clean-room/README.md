# RID zoom-cover clean-room audit

## Summary

This directory contains an externally authored, source-isolated audit of Hervay's 38 zoom-cover inputs.
The strict result is **inconclusive**.
The article states the mathematics, but it does not define the compact "rid-cover/1" serialization.
The checker refuses to guess the missing vertex indices, inequality indices, tree grammar, or coordinate binding.

The copied inputs contain 11,183 witness leaves and 48 delegated leaf records.
These are derived inventory counts.
They are not mathematically checked cell counts.

## Result

The implementation independently passed 55 primitive and mutation tests.
It also checked the exact input inventory, Appendix B parameters, the arc-plane support equality, and the pentagon domain identity.

It did not reconstruct any serialized terminal cell or witness.
Therefore it did not check the five per-cell zoom obligations.
The result is neither confirmation nor disagreement with the proof.

The implementation was source-isolated before the freeze.
It was not result-blinded.
The Maths Search front door disclosed aggregate results before work began.

See:

- [SPECIFICATION.md](SPECIFICATION.md) for the article-derived mathematics and exact blockers;
- [FREEZE.md](FREEZE.md) for the immutable pre-comparison state;
- [results/clean-room-result.json](results/clean-room-result.json) for the machine-readable result;
- [results/comparison.json](results/comparison.json) for the post-freeze comparison.

## Reproduce

Requirements:

- Python 3.8 or later;
- a POSIX environment with Zsh and "tee";
- no third-party Python packages.

Run from any directory:

    /Users/davidryan/code/projects/rid-nopert-audit/clean-room/run.sh

The command disables user-site packages, runs the full unit suite, and rebuilds the JSON result.
It captures standard output and errors in "results/run.log".

To require a mathematical pass, run:

    PYTHONPATH=src python3 src/checker.py --require-pass

That command returns status 2 for the frozen inconclusive result.

## Clean-room boundary

Before "FREEZE.md" existed, the session read only:

- "/Users/davidryan/hq/AGENTS.md";
- the Maths Search project front door;
- the copied article at the pinned commit;
- the 38 copied declarative cover files.

Before the freeze, it did not read or execute:

- the existing RID audit document;
- the audit repository report, manifest, or logs;
- upstream "proof/src", tests, validation, figures, audit code, or build script;
- any existing zoom checker;
- any prior temporary audit directory.

The permitted article and JSON inputs were copied from a fresh detached checkout.
All later clean-room work stayed in this directory.

## Directory layout

- "inputs/article.pdf": the permitted article;
- "inputs/local": the 30 permitted Local inputs;
- "inputs/exotic": the eight permitted Exotic inputs;
- "src": independent exact primitives and the fail-closed checker;
- "tests": hand-computed unit tests and mutation controls;
- "results": hashes, captured runs, and structured results;
- "research/article.txt": a local text extraction of the permitted article.

No upstream source file was copied into this directory.

## Independent implementation

The implementation uses:

- "fractions.Fraction" for rational arithmetic;
- an explicit pair representation for \(\mathbb Q(\sqrt5)\);
- sparse multivariate polynomials;
- exact general substitution;
- exact monomial division;
- an independent tensor power-to-Bernstein conversion;
- exact corner bounds and interval products;
- explicit midpoint-tree validation;
- exact RID coordinate generation and support comparisons.

The code shares mathematical definitions with upstream through the article.
It shares no source code or third-party dependency with upstream.

## Remaining assumptions

The syntactic validator treats the visible two-entry coefficient arrays as \((a,b)\).
This agrees with Section 5.1, but "rid-cover/1" has no public schema.

The Appendix B consistency check compares visible shape fields with the article's tables.
It does not assign proof semantics to compact trees, witness indices, factors, or delegation markers.

Every missing semantic definition is listed in "SPECIFICATION.md".
The checker reports each omission and marks every dependent obligation as blocked.

## Recommended next process

Use two separate sessions.

1. A specification session can inspect Hervay's source and produce a neutral declarative schema.
2. A new implementation session can receive only that schema, the article, and the 38 JSON files.

The neutral schema must include provenance for each extracted definition.
The new implementation session must not see the original checker source.

A checker that reads the original implementation before its freeze is an independent reimplementation.
It is not a strict clean-room checker.
