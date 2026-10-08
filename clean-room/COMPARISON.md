# Post-freeze comparison

## Summary

The frozen strict checker remained inconclusive because the public material omits eleven `rid-cover/1` definitions.
A fresh pinned upstream run passed all four exhaustive partitions and verified 11,183 witness cells.
Every per-cover witness count matched the frozen input inventory.

## Run

- **Commit:** `802a3ded09535c4a99cef1371ce0d0277c433fa8`
- **Checkout:** fresh and detached
- **Rust:** 1.99.0
- **Command:** `cargo test --release --lib proof::tests::independent_verification_of_every_cell -- --ignored --test-threads=4 --nocapture`
- **Result:** four passed, zero failed
- **Cells:** 11,183
- **Test time:** 515.96 seconds
- **Wall time with compilation:** 551.04 seconds
- **Log:** `results/upstream-zoom.log`

The frozen inputs contain 11,183 witness leaves and 48 delegated leaves.
The upstream cell total counts witness leaves.
Its independent model also checks each delegated record before partitioning the witness jobs.

## Special cases

| Case | Count | Post-freeze upstream result |
|---|---:|---|
| `crossing+` delegated leaves | 34 | Hand-over passed |
| `crossing-` delegated leaves | 14 | Hand-over passed |
| Domain-witness leaves | 450 | Indexed domain polynomials passed |
| Pentagon extension | One cover | Exact beyond-face check passed |

The hand-over checks window containment, target selection, target-root containment and configuration equality.
The pentagon check binds cover axis 1 to domain inequality 0.

## Learned only after the freeze

The source supplied every missing convention.

1. `problem/geometry/mod.rs` sorts literal vertex codes lexicographically.
2. `problem/domain/mod.rs` defines all 73 inequality indices.
3. `zoom/tree/mod.rs` defines preorder midpoint trees, lower child first, with `.` as a leaf.
4. The cover code generates zoom families and names in a fixed face order.
5. Tube, A, B and sheared zooms define their five variable orders and factor positions.
6. The affine map uses rows as output coordinates and columns as cover coordinates.
7. The witness parser binds each JSON field to its mathematical role.
8. Base-face radii follow axis order, with the lower face before the upper face.
9. The window vector selects a sheared target for each delegated leaf.
10. `beyond` binds a cover axis to a domain inequality.
11. The format module requires typed, canonical JSON and rejects unknown fields.

These rules are implementation definitions.
The article and copied proof data do not state them.

## Classification

The strict clean-room result is **inconclusive due to an incomplete public specification**.
The upstream result is **passed**.
The two results contain no numerical or mathematical contradiction.

The upstream pass cannot complete the frozen clean-room proof because it supplies the missing semantics from prohibited source.
The public audit verdict remains unchanged.

## Recommended next process

Use two separate sessions.

1. A specification session extracts a neutral `rid-cover/1` specification with provenance for every definition.
2. A new implementation session receives only that specification, the article and the 38 JSON files.

The machine-readable comparison, including all 38 per-cover counts, is in `results/comparison.json`.
