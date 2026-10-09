# `rid-cover/1` clean-room checker

## Summary

This directory contains an independent exact checker for the 38 `rid-cover/1` files. It uses only Python's standard library.

## Implementation Checklist

- [x] Authenticate the specification bundle.
- [x] Record the clean-room boundary and every permitted input hash.
- [x] Implement canonical JSON and semantic schema checks.
- [x] Regenerate vertices, cover families, zoom names, roots, and variable order.
- [x] Implement exact arithmetic in `Q(sqrt(5))`.
- [x] Reconstruct zoom maps, cell trees, witnesses, exact factors, and Bernstein coefficients.
- [x] Check support, domain scope, delegated hand-over, and pentagon extension rules.
- [x] Add independent unit and mutation tests.
- [x] Run and freeze the complete 38-file result.

## Commands

```text
python3 -m unittest -v test_checker.py
python3 checker.py --all --output RESULT-MANIFEST.json
```

The checker accepts only the fixed specification directory and the two permitted input directories recorded in `BOUNDARY.md`.
