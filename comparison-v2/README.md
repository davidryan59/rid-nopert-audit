# Post-freeze comparison of the `rid-cover/1` checker

## Summary

**Final status: confirmed.** The frozen, source-isolated checker conforms to
`rid-cover/1-spec.1`. The neutral specification faithfully describes the
pinned upstream implementation. A source-only reproduction passed all 13
tests and all 38 cover files. Its non-runtime result matched the frozen result
exactly.

The comparison found no invalid cover, specification defect, frozen-checker
defect, or upstream implementation defect. It found one counting phrase to
correct in the earlier audit. The number 11,183 counts witness leaves. The 48
delegated leaves give 11,231 terminal leaves in total. This was a presentation
defect and had no effect on the proof verdict.

## Checkpoint and evidence boundary

The pre-comparison Git commit was
`5e82692009619507f47d4a915aa5868e03fe6e31`. The checkpoint ran on 2026-10-09
under macOS 26.6.2, Darwin 25.6.0 arm64, in the Asia/Ho_Chi_Minh time zone,
with Python 3.8.13.

The frozen evidence set is defined by the checksum file and manifests. Git
tracking and ignore rules do not enlarge that set.

| Evidence | SHA-256 |
|---|---|
| [`specification/SHA256SUMS`](../specification/SHA256SUMS) | `5f0f6e67a0ba7cf121750aa1ef4f09b86896303adcda467e2216b7f918e5296f` |
| [`clean-room-v2/SOURCE-MANIFEST.sha256`](../clean-room-v2/SOURCE-MANIFEST.sha256) | `3d8cca95ce326b8835104171fe0ed16d67d5b5895767b5ddd424546ba085abc7` |
| [`clean-room-v2/RESULT-MANIFEST.json`](../clean-room-v2/RESULT-MANIFEST.json) | `f9791caaf628ff79d6c9b6a680cca1aefeec748d6d7c154a51322ed65371c8b4` |
| [`clean-room-v2/INPUT-MANIFEST.sha256`](../clean-room-v2/INPUT-MANIFEST.sha256) | `3e7361ad7567d40cc2eb561b5e7a28014acbb65e68b284a246b65d85090bf8c3` |
| [`clean-room-v2/FROZEN-SHA256SUMS`](../clean-room-v2/FROZEN-SHA256SUMS) | `7e9d36d44d00f33c8f2847711aa3d349ecfcf47dfd6584b5d8386e5b61af085c` |

Every nested checksum in those files passed. The frozen result contains 38
passing results, no diagnostic, and the following exact totals:

| Metric | Total |
|---|---:|
| Terminal leaves | 11,231 |
| Witness leaves | 11,183 |
| Delegated leaves | 48 |
| Corner evaluations | 357,856 |
| Bernstein coefficients | 1,260,757 |

### Preliminary procedural stop

An earlier response stopped because two ignored Python cache files were not
tracked by Git. That requirement was incorrect. The files were outside every
frozen manifest and could not change an accepted input, specification,
executed source, recorded result, or information boundary.

This was a procedural stop, not an audit finding or mathematical uncertainty.
The cache files remain ignored and untracked. No ignore rule was changed.

## Source-only reproduction

The repeated reproduction used a fresh directory. It copied only
`checker.py` and `test_checker.py` from the source-manifest set. The directory
initially had no `__pycache__` directory and no `.pyc` file. Both commands used
Python's `-B` option and disabled bytecode writes.

The complete unit and mutation suite passed all 13 tests. The full checker
then passed all 38 cover files. It produced the same totals shown above.
The reproduced JSON had SHA-256
`a3bb8bbd8b5522820ac58f34ba2f98380002ee7037b2d6a2aae2e2d13feb95ec`.
Its runtime was 1,439.177905 seconds.

An independent structural comparison removed runtime fields and compared
every other field. It found no difference in paths, input hashes, verdicts,
diagnostics, counts, or verification metrics. No bytecode cache appeared
before or after either run.

## Specification fidelity

The comparison used upstream commit
`802a3ded09535c4a99cef1371ce0d0277c433fa8`. A fresh detached checkout matched
all 16 source hashes in
[`PROVENANCE.json`](../specification/PROVENANCE.json). The 38 accepted cover
files were byte-identical to the pinned upstream files.

An independent generator reconstructed all 60 vertices, all 60 symmetry
folding polynomials, and all 73 domain polynomials from the pinned source.
Every generated object matched the specification exactly.

| Specification area | Comparison result |
|---|---|
| Vertex numbering | Exact match to the lexical literal-code order. |
| Domain-inequality numbering | Exact match for all 73 inequalities. |
| Affine-map convention | Exact match to `x_i = c_i + sum_j M_ij z_j`. |
| Adapted coordinate systems | Exact match to the source compositions. |
| Zoom inventory and ordering | Exact match for all families and 334 roots. |
| Zoom-variable ordering | Exact match, including scale positions. |
| Face and radius ordering | Exact match: axes increase, lower then upper. |
| Tree grammar and leaf association | Exact preorder and child association. |
| Witness semantics and Bernstein sign | Exact witness gap and strict negative sign. |
| Delegated hand-over | Exact window, gauge, target, and map semantics. |
| Pentagon extension and JSON encoding | Exact extension and canonical schema. |

The specification uses declarative text, equations, tables, and data. It does
not copy Rust source. Its semantics were derived from the pinned upstream
implementation, as its provenance record states.

## Frozen checker audit

The checker implements exact arithmetic in `Q(sqrt(5))`, polynomial pullback,
exact monomial division, and Bernstein conversion. It regenerates the domain
and symmetry data, all 60 vertices, all 120 edges, every cover family, and all
334 zoom roots.

It enforces the canonical JSON schema, input hashes, catalogue order, tree
grammar, leaf binding, witness indices, support conditions, strict Bernstein
signs, delegated windows, hand-over maps, and the pentagon extension. It
rejects missing, extra, malformed, non-canonical, or inconsistent data. The
six mutation cases in the 13-test suite exercise these fail-closed paths.

No required obligation was absent. No repair or new clean-room version is
needed.

## Comparison with other evidence

| Evidence | Verdict | Relationship to the frozen result |
|---|---|---|
| Initial article-only clean room | Inconclusive | It parsed 11,231 leaves but lacked eleven encoding conventions. |
| Frozen `rid-cover/1` checker | Pass | It verified all 38 files and every terminal leaf. |
| Source-only reproduction | Pass | It matched every non-runtime result field. |
| Pinned upstream checker | Pass | It accepted the same cover data. |
| Upstream exhaustive second model | Pass | It rebuilt all 11,183 witness leaves. |
| Original audit reproduction | Pass | It accepted all 192,696 certificate records. |
| Regenerated certificate | Pass | It was byte-identical to the supplied certificate. |

The per-file comparison is recorded in
[`comparison.json`](comparison.json). All 38 verdicts agree. Each upstream
witness count equals the independent witness count. The frozen checker also
records exact corner and Bernstein totals that the retained upstream summary
does not expose.

Cargo was unavailable in the comparison shell, so this session did not repeat
the upstream Rust run. It used the retained pinned-commit run, the successful
original reproduction, and a fresh detached checkout whose 16 relevant source
hashes all matched the provenance record.

## Count reconciliation

The cover trees have 11,231 terminal leaves. Of these, 11,183 carry direct
witnesses and 48 delegate to another zoom. The upstream exhaustive test named
in the earlier report processes witness leaves, so its 11,183 count is not the
terminal-leaf total.

The retained [upstream run log](../clean-room/results/upstream-zoom.log) lists
the per-file witness counts. The [first comparison record](../clean-room/results/comparison.json)
reconciles those counts with 34 positive-crossing and 14 negative-crossing
delegations. The pinned
[`independent_verification` test](https://github.com/bence-hervay/nopert-rid/blob/802a3ded09535c4a99cef1371ce0d0277c433fa8/proof/src/elimination/proof/tests.rs)
selects witness leaves for that campaign.

Upstream validates delegated leaves through the cover loader and separate
[`adversarial` tests](https://github.com/bence-hervay/nopert-rid/blob/802a3ded09535c4a99cef1371ce0d0277c433fa8/proof/src/elimination/proof/tests/adversarial.rs).
Those checks cover each hand-over window and its target map. The frozen checker
independently validates all 48 delegated leaves.

Earlier uses of “11,183 zoom cells” could imply the full terminal count. The
root README, audit report, and machine manifest now use the three distinct
terms. Historical logs remain unchanged as records of their runs.

## Adjudication

| Difference | Classification | Effect |
|---|---|---|
| The earlier report called 11,183 witness leaves “zoom cells”. | Previous-audit defect. | The corrected total is 11,231 terminal leaves. The effect is presentational, and the proof verdict is unchanged. |
| Reproduction runtimes differ. | Harmless runtime difference. | No effect on any compared field or verdict. |

No disagreement belongs to the invalid-cover, specification-defect,
frozen-checker-defect, upstream-defect, or unresolved classes.

The evidence supports five separate conclusions:

- The checker conforms to `rid-cover/1-spec.1`.
- The specification is faithful to the pinned implementation.
- The 38 serialized proof files satisfy the specified obligations.
- The independent and upstream checkers agree on verdicts and exposed counts.
- The article, certificate, original audit, and cover checks support the stated
  Nopert theorem under the report's execution and arithmetic assumptions.

## Integrity and publication status

The post-comparison checksum pass reproduced all five hashes in the checkpoint
table and passed every nested checksum. No tracked file under
`clean-room-v2/` changed. Its source-manifest and result-manifest hashes remain
unchanged.

The publication report now explains the specification-mediated clean-room
verification. It also records the source-isolated implementation and the
separate post-freeze comparison. No further corrective work is required before
publication. The report's stated platform, compiler, arithmetic-library, and
source-provenance assumptions remain.
