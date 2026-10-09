# Clean-room boundary

## Summary

This workspace contains an independent exact checker for `rid-cover/1`. The implementation session began on 2026-10-08.

## Permitted inputs

- Every file in `/Users/davidryan/code/projects/rid-nopert-audit/specification/`.
- `/Users/davidryan/code/projects/rid-nopert-audit/clean-room/inputs/article.pdf`.
- The 38 JSON files in `/Users/davidryan/code/projects/rid-nopert-audit/clean-room/inputs/local/` and `/Users/davidryan/code/projects/rid-nopert-audit/clean-room/inputs/exotic/`.
- Mandatory system and repository instructions supplied automatically.

## Prohibited inputs

- Existing clean-room source, tests, reports, logs, or documentation.
- The original or any previous checker.
- Audit reports, comparison reports, and manifests outside the specification bundle.
- The upstream implementation, tests, validation data, and figures.
- Git history or diffs that expose prohibited materials.
- Repositories and source paths named in `PROVENANCE.json`.
- The specification session's conversation and working notes.
- Internet sources.

## Session rule

No prohibited material may be inspected before or after the freeze in this session. This session performs no upstream comparison.
