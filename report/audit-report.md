# Independent Audit of the Nopert Certificate for the Rhombicosidodecahedron

**David Ryan**  
Version 0.1.0, 2026-10-09<br>
DOI: [10.5281/zenodo.23232399](https://doi.org/10.5281/zenodo.23232399)

## Abstract

Bence Hervay announced a computer-assisted proof that the
rhombicosidodecahedron has no Rupert passage. This report gives an independent
mathematical and computational audit of that claim. It uses *Nopert* for a
solid without Rupert's property.

The audit examined the mathematical reduction before running the supplied
programs. It then reproduced the Rust checker and Python audit from commit
`802a3ded09535c4a99cef1371ce0d0277c433fa8`. Both accepted all 192,696
certificate records. A clean Rust search regenerated the 18,195,036-byte
certificate exactly. Its SHA-256 hash matched the supplied certificate.

The review concentrated on the zoom lemma and the reduction from all possible
passages to a finite local cover. No mathematical gap was found. The
repository's exhaustive second Rust model rebuilt all 11,183 witness leaves.
A source-isolated checker also validated the 48 delegated leaves, for 11,231
terminal leaves in total.

> **Outcome: confirmed subject to stated assumptions.**

The specification-mediated clean-room verification checked all 38 zoom covers
with a fresh implementation. Its neutral specification was derived from the
pinned upstream implementation. The implementation had no access to upstream
source, earlier checker source, audit verdicts, or comparison material before
its result was frozen.

## 1. Scope and disclosure

This report audits Hervay's stated theorem, its mathematical reduction, its
exact certificate, and the supplied checking software. It does not assess the
result's novelty or every historical statement in the article.

This is an independent technical audit. It is not peer review or a formal
proof. Independent means that the audit was conducted separately from the
author and reasoned from the mathematical argument before trusting program
outputs.

David Ryan directed the audit. OpenAI Codex using GPT-5.6 Sol at Extra High
reasoning performed the mathematical review, source inspection, computational
reproduction, adversarial analysis, and first report draft on 2026-10-08.

Every quantitative claim below comes from an executable check, retained output,
or named source file. The repository accompanying this report records the
commands, hashes, environment, and limitations.

## 2. Audited material

- Bence Hervay, *Non-Rupertness of the Rhombicosidodecahedron*, 58 pages.
- Repository: [bence-hervay/nopert-rid](https://github.com/bence-hervay/nopert-rid).
- Audited commit: [`802a3ded09535c4a99cef1371ce0d0277c433fa8`](https://github.com/bence-hervay/nopert-rid/commit/802a3ded09535c4a99cef1371ce0d0277c433fa8).
- Projection source: Steininger and Yurkevich,
  [*An algorithmic approach to Rupert's problem*](https://arxiv.org/abs/2112.13754).

The checkout had no tag at its head. The full commit identifies the audited
version.

| Input | SHA-256 |
|---|---|
| `paper/article.pdf` | `e52022737fad1f5add102b8a8b357788a3c5086111f028255a6e7a26d6bd71ff` |
| `proof/results/full/search.cert` | `df1f8dbab68b561f22fa9daeca48153d71bde7b6fba3345d9f6b7b8077df4b5f` |
| `proof/Cargo.lock` | `2f40f55632dcbccd722fcd2681153f1f5472984680680d3346dbcee4dbb1bd24` |
| `audit/uv.lock` | `2ea8eda0baf9f33ef03a0a8c946860b2f3def1eaffe154ba27d22f9b4f4bc44b` |

## 3. Audit method

The audit used five layers.

First, it read the article's argument and traced each reduction into the code.
This review covered projected containment, centring, symmetry, branch and
bound, exact arithmetic, local exclusions, and certificate completeness.

Second, it built and ran the supplied Rust checker and Python audit from a
clean checkout. The environments used locked Rust and Python dependencies.

Third, it regenerated the complete certificate with the Rust search. A byte
comparison tested whether the clean search reproduced the supplied object.

Fourth, it attacked the proof's choke points. The audit inspected cover
completeness, divisibility factors, no-fit sets, support conditions, hand-over
maps, and domain extensions. It also ran the repository's exhaustive second
cover model and the supplied mutation controls.

Fifth, a specification-mediated clean-room verification implemented the cover
format from a neutral specification. A separate post-freeze session compared
that checker with the pinned implementation and the earlier audit.

## 4. Mathematical audit

### 4.1 Projection and centring

The projection criterion reduces a straight passage to strict containment of
two planar shadows. Central symmetry then removes planar translation. The
midpoint proof of the centring lemma works for ordinary and strict containment.

The margin function correctly expresses scaled radial containment. It varies
continuously because each shadow has finitely many projected vertices. Aligned
configurations have margin one. Excluding every strict fit therefore proves
the Nopert result.

The projection and centring reductions agree with Propositions 1 and 2 of
Steininger and Yurkevich.

### 4.2 Symmetry-reduced domain

The viewing-line reduction uses all 120 orthogonal body symmetries. Their
retained half-spaces give the stated triangular viewing cone.

The relative rotation reduction compares the rotation with its images under
the full icosahedral rotation group and the central half-turn. The necessary
comparisons ensure that every physical configuration has a representative in
the closed domain `D`.

The proof only needs `D` to contain one representative of every configuration.
Uniqueness and minimality are unnecessary.

### 4.3 Global component

A projected plug vertex beyond a valid support line excludes containment. The
support normal remains perpendicular to the changing view. Exact Bernstein
signs certify separation throughout each closed search box.

The final certificate does not depend on the Rust checker's support shortcut.
The Python replay validated the full sixty-member maximum form for all 157,458
Global records. The shortcut also held for 908 records.

### 4.4 Zoom lemma

The zoom lemma is sound when five obligations hold:

1. Each divided coordinate is non-negative on the cell.
2. Its zero set maps into a proved no-fit set.
3. The pulled-back witness is exactly divisible by the stated monomial.
4. Every support condition holds at each required corner view.
5. Every Bernstein coefficient of the quotient has the required strict sign.

The corner step is valid because each support condition is multi-affine in the
zoom coordinates. Its minimum on a box occurs at a corner. Exact division
removes only non-negative distance factors. A zero factor places the
configuration in the applicable no-fit set.

The implementation checks each obligation. It rejects negative scale ranges,
wrong factors, failed exact division, non-positive views, invalid supports,
and non-strict quotient signs.

### 4.5 No-fit sets and local covers

The aligned set contains no fit because both shadows coincide. The two arc
planes contain no fit because both shadows have the same support value in the
screen direction `e2`.

Tube coverage normalises each non-zero offset on a face of its sign box. Point
coverage divides cases by the ratio of offset size to base size. Together they
cover the stated product box, including the shared boundary.

The crossing hand-over is complete. Each delegated first-arc cell maps to the
same physical configuration in a sheared second-arc zoom. The exact window
test keeps the image inside that zoom's root.

The pentagon cover extends beyond one face of its proved region. The code
checks that domain inequality zero is a positive multiple of the distance
beyond that face. The extension therefore contains only points outside `D`.

### 4.6 Reduction to a finite certificate

The binary certificate leaves cover the whole five-dimensional root box. The
proof uses two checked facts for every leaf:

- The leaf belongs to a sound elimination component.
- The leaves form a complete, prefix-free binary cover of the root.

These facts close the risk of an unlisted passage between local models. Any
passage would lie in a certificate leaf. That leaf's exact component proof
would give a contradiction.

## 5. Reproduction results

| Check | Result |
|---|---|
| Certificate framing | 192,696 records; 18,195,036 bytes; final newline present |
| Component counts | 12,650 Domain; 157,458 Global; 21,792 Local; 796 Exotic |
| Rust checker | `complete:true`; zero frontier; 192,696 records accepted |
| Rust checker time | 49.26 seconds |
| Python record replay | 192,696 accepted; zero refused; 116 seconds |
| Python structure check | Prefix-free; complete; Kraft sum one; 20,000 probes covered |
| Clean Rust search | 385,391 boxes evaluated; 192,696 records; 89.764 seconds |
| Search comparison | Byte-identical to the supplied certificate |
| Ordinary Rust tests | 393 proof and integration tests passed |
| Exhaustive second cover model | Four partitions passed; 11,183 witness leaves accepted |
| Source-isolated cover checker | 13 tests and 38 files passed; 11,231 terminal leaves validated |

The regenerated certificate had SHA-256
`df1f8dbab68b561f22fa9daeca48153d71bde7b6fba3345d9f6b7b8077df4b5f`.
This matched the supplied certificate.

The Python replay output had SHA-256
`bf46d5c27f030c893c67bf9b467e00fd700acc5fe684478da22db3e038790a07`.

The first audit ran on Darwin 25.6.0 arm64. It used Rust and Cargo 1.99.0,
Python 3.14.6, NumPy 2.5.3, and python-flint 0.9.0. The temporary checkout,
toolchains, build outputs, and caches used less than 1 GB.

## 6. Adversarial checks

The supplied Python controls made the following attacks:

- 4,800 Global witnesses on boxes containing an aligned rotation produced
  zero false acceptances.
- 400 Global witnesses on boxes containing a symmetry rotation produced zero
  false acceptances.
- 10,950 Domain claims on boxes containing a point of `D` produced zero false
  acceptances.
- 11,400 cover-containment probes produced zero disagreements with corner
  sampling.
- Foreign, reversed, and enlarged Global witnesses failed unless the witness
  remained valid.

The Rust tests mutate records, witnesses, checksums, cover cells, tilings,
factors, zoom maps, window delegations, and inclusion boxes. The checker
refused corrupt inputs or independently confirmed the surviving claim.

The exhaustive ignored test reconstructs each witness leaf from its
definitions. It rebuilds zoom families, witness polynomials, monomial division,
Bernstein coefficients, cell trees, and the pentagon extension. All four
partitions passed in 515.21 seconds. The cover loader and separate adversarial
tests validate the 48 delegated leaves and their hand-over maps.

## 7. Clean-room method and independence

The first clean-room attempt used only the article and the 38 serialized cover
files. Its [freeze record](../clean-room/FREEZE.md) preserved an inconclusive
result. Its [working specification](../clean-room/SPECIFICATION.md) could parse
the trees and count 11,231 leaves, but it could not assign mathematical meaning
to every field.

That attempt identified eleven missing `rid-cover/1` conventions:

1. vertex numbering;
2. domain-inequality numbering;
3. affine-map convention;
4. adapted coordinate systems;
5. zoom inventory and ordering;
6. zoom-variable ordering;
7. face and radius ordering;
8. tree grammar and leaf association;
9. witness semantics and Bernstein sign;
10. delegated hand-over; and
11. pentagon extension and complete JSON encoding.

A separate specification session inspected the pinned upstream source. It
produced the neutral [`rid-cover/1-spec.1`](../specification/RID-COVER-SPEC.md)
specification. The package records its
[`provenance`](../specification/PROVENANCE.json),
[`version`](../specification/VERSION.json), and
[`checksums`](../specification/SHA256SUMS). It supplied declarative rules,
canonical data tables, the version record, provenance, and hashes. The
specification manifest has SHA-256
`5f0f6e67a0ba7cf121750aa1ef4f09b86896303adcda467e2216b7f918e5296f`.

The fresh implementation session could read that package, the article, and the
38 accepted input files. It could not read upstream source, the first checker,
previous audit reports or verdicts, or comparison material. Its
[`boundary record`](../clean-room-v2/BOUNDARY.md) states these controls. The
implementation was source-isolated. Its neutral specification was derived
from the pinned upstream implementation, so this second checker was not an
article-only checker.

Before comparison, the session passed 13 unit and mutation tests and all 38
cover files. The [`freeze record`](../clean-room-v2/FREEZE.md),
[`run record`](../clean-room-v2/RUN-RECORD.md), and
[`result manifest`](../clean-room-v2/RESULT-MANIFEST.json) preserve that
outcome. The source-manifest hash is
`3d8cca95ce326b8835104171fe0ed16d67d5b5895767b5ddd424546ba085abc7`.
The result-manifest hash is
`f9791caaf628ff79d6c9b6a680cca1aefeec748d6d7c154a51322ed65371c8b4`.
The full frozen checksum record is
[`FROZEN-SHA256SUMS`](../clean-room-v2/FROZEN-SHA256SUMS).

The pre-comparison result was a pass. It verified 11,183 witness leaves and 48
delegated leaves, which give 11,231 terminal leaves. It performed 357,856
corner evaluations and checked 1,260,757 Bernstein coefficients.

The post-freeze comparison first repeated the checker from a fresh source-only
temporary copy. It used Python's `-B` option and created no bytecode cache. The
13 tests and all 38 files passed again. Every non-runtime field matched the
frozen result.

Only then did the comparison inspect upstream and previous audit material. It
checked all eleven conventions against commit
`802a3ded09535c4a99cef1371ce0d0277c433fa8`. It also audited every checker
obligation and fail-closed path. The detailed
[`comparison report`](../comparison-v2/README.md) and
[`machine record`](../comparison-v2/comparison.json) record the evidence.

The comparison confirmed the checker, specification, and 38 proof files. It
also corrected one earlier phrase. The number 11,183 is the witness-leaf
count. The 48 delegated leaves bring the terminal total to 11,231. This
wording correction does not change the verdict.

The preliminary procedural stop concerned ignored `.pyc` cache files outside
the frozen evidence set. Those files could not affect an input, specification,
executed source, result, or information boundary. The source-only reproduction
resolved the execution question. The stop was not an audit finding.

Post-comparison checks confirmed every frozen hash. No tracked file under
`clean-room-v2/` changed. The remaining uncertainty is limited to the general
execution, arithmetic-library, and provenance assumptions stated below.

## 8. Qualifications and assumptions

The default Rust test command reported two failures on the audit Mac. One test
uses Linux `prlimit`, which macOS lacks. One scheduler performance test crossed
its timing threshold in the sandbox. Both concern failure handling or worker
utilisation. Neither enters the mathematical proof checker.

Every other ordinary unit and integration test passed after those exclusions.
The proof-relevant exhaustive test also passed.

The original Python checker independently verifies certificate records,
framing, and coverage. It treats the zoom-cover cell proofs as checked inputs.
The upstream exhaustive Rust model rebuilds the witness leaves while sharing
the repository's arithmetic layer. The source-isolated checker removes that
shared-code dependence for all 38 serialized covers.

The verdict assumes:

- The audited commit is the version attached to the announced claim.
- Rust's `num` crates correctly implement arbitrary-precision arithmetic.
- Python FLINT correctly implements integer and rational arithmetic.
- The operating system and compiler executed the checked source faithfully.

Cross-language and source-isolated agreement reduce arithmetic and
implementation risk. A formal kernel would provide stronger assurance.

## 9. Conclusion

The mathematical reduction survived adversarial review. Both supplied
checkers accepted every certificate record. The clean search reproduced the
certificate exactly. The upstream second model accepted every witness leaf.
The source-isolated checker validated every witness and delegated leaf.

The audit therefore confirms Hervay's proof that the rhombicosidodecahedron is
Nopert, subject to the stated assumptions.

The specification-mediated clean-room verification confirms all 38 covers.
Its post-freeze comparison found no unresolved discrepancy. The remaining
assumptions concern provenance and faithful execution of exact arithmetic.

## References

1. Bence Hervay. *Non-Rupertness of the Rhombicosidodecahedron*. Source and
   proof repository, audited commit `802a3ded09535c4a99cef1371ce0d0277c433fa8`,
   2026.
2. Jakob Steininger and Sergey Yurkevich. *An algorithmic approach to Rupert's
   problem*. arXiv:2112.13754, 2021. Revised publication metadata appears on
   the arXiv record.
