# Independent audit of the RID Nopert proof

This repository records an independent technical audit of Bence Hervay's
computer-assisted proof that the rhombicosidodecahedron is Nopert. The audit
examined the mathematical reduction, reproduced both supplied checkers, and
regenerated the complete certificate.

**Outcome: confirmed subject to stated assumptions.**

The result applies to Hervay's repository commit
`802a3ded09535c4a99cef1371ce0d0277c433fa8`. The audit found no mathematical
gap in the projection reduction, symmetry reduction, zoom lemma, or finite
cover.

This is an independent technical audit. It is not peer review or a formal
proof. The report states the assumptions and remaining assurance gap.

## Original work

- Announcement: [Bence Hervay on X](https://x.com/BenceHervay/status/2107533555199091089)
- Proof repository: [bence-hervay/nopert-rid](https://github.com/bence-hervay/nopert-rid)
- arXiv article: pending

## Contents

- [`report/audit-report.pdf`](report/audit-report.pdf): the publication copy.
- [`report/audit-report.md`](report/audit-report.md): the report source.
- [`manifest.json`](manifest.json): machine-readable inputs, hashes, commands,
  results, and environment details.
- [`logs/audit-run.json`](logs/audit-run.json): the recorded first audit run.
- [`scripts/reproduce.sh`](scripts/reproduce.sh): a clean, full reproduction.
- [`scripts/build-report.sh`](scripts/build-report.sh): the PDF build.

The repository does not redistribute Hervay's article, certificate, or source.
The reproduction script checks out the exact upstream commit and verifies its
recorded hashes.

## Reproduce the audit

The full run needs Git, a recent Rust toolchain, Python 3.10 or later, and
[`uv`](https://docs.astral.sh/uv/). It takes about 15 minutes on the machine
used for the first audit. The script creates a new working directory and
writes complete logs there.

```sh
./scripts/reproduce.sh
```

Pass a new directory when the default `work` directory already exists:

```sh
./scripts/reproduce.sh work-2
```

The run checks the certificate, runs both checker implementations, regenerates
the certificate, compares it byte for byte, and rebuilds all 11,183 zoom cells.

The complete runner passed from a separate checkout on 2026-10-08. It accepted
all 192,696 records, passed 393 ordinary tests, accepted all 11,183 zoom cells,
and regenerated the certificate byte for byte.

## Rebuild the report

The report build needs Pandoc and Chrome or Chromium:

```sh
./scripts/build-report.sh
```

## Method disclosure

David Ryan directed the audit. OpenAI Codex using GPT-5.6 Sol at Extra High
reasoning performed the mathematical review, source inspection, reproduction,
adversarial analysis, and first report draft on 2026-10-08.

The model read the mathematical argument before treating the programs as
authoritative. It then tried to break the zoom lemma and the reduction to the
finite cover. Every quantitative claim in the report is tied to an executable
check, a recorded output, or a named mathematical argument.

## Citation

Version `0.1.0` is the first-pass audit. Use [`CITATION.cff`](CITATION.cff) for
repository metadata.

- All versions: [10.5281/zenodo.23232398](https://doi.org/10.5281/zenodo.23232398)
- Version `0.1.0`: [10.5281/zenodo.23232399](https://doi.org/10.5281/zenodo.23232399)

Please cite Hervay's proof separately. This audit evaluates that work and does
not claim its theorem or certificate as original work.

## Licences

The report and audit metadata use CC BY 4.0. The original scripts in this
repository use the MIT Licence. See [`LICENSE.md`](LICENSE.md).
