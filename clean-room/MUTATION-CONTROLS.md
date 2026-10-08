# Mutation controls

## Summary

The suite tests every obligation that the public material defines independently of "rid-cover/1".
Controls that need the missing serialization semantics remain blocked and are listed explicitly.

## Completed controls

| Requested mutation | Fixture | Detection |
|---|---|---|
| Missing leaf | Synthetic explicit subdivision tree | Missing child rejected |
| Duplicated leaf | Synthetic explicit subdivision tree | Duplicate identifier rejected |
| Overlapping or malformed child pair | Synthetic explicit subdivision tree | Exact midpoint box mismatch rejected |
| Enlarged cell | Synthetic explicit subdivision tree | Exact midpoint box mismatch rejected |
| Changed root bound | Copied Local input fixture | Appendix B comparison rejected it |
| Wrong distance factor | Hand-computed polynomial | Exact division rejected it |
| Omitted factor | Hand-computed polynomial | A zero Bernstein coefficient rejected it |
| Incorrect exponent | Hand-computed polynomial | Exact division rejected it |
| Perturbed witness coefficient | Hand-computed polynomial | A negative Bernstein coefficient rejected it |
| Failed exact division | Hand-computed polynomial | Residual monomial rejected |
| Invalid support corner | Hand-computed multi-affine support | Exact corner minimum rejected it |
| Zero Bernstein coefficient | Hand-computed quotient | Strict sign test rejected it |
| Negative Bernstein coefficient | Hand-computed quotient | Strict sign test rejected it |
| Enlarged hand-over window | Copied crossing input fixture | Article radius comparison rejected it |
| Invalid pentagon extension descriptor | Copied pentagon input fixture | Article parameter comparison rejected it |
| Unknown field | Copied Local input fixture | Exact-key schema check rejected it |
| Malformed rational field | Copied Local input fixture | Rational grammar rejected it |

The positive controls include the valid synthetic trees and polynomials.
They also include reordered JSON members and an equivalent rational spelling.

## Blocked controls

These requested controls cannot be attached to the copied proof data without guessing.

| Requested mutation | Missing public definition |
|---|---|
| Missing or duplicated serialized tree leaf | Tree grammar and leaf-array association |
| Broken hand-over target | A "delegated" leaf contains no target reference |
| Coordinate permutation | Matrix orientation and zoom coordinate order |
| Changed serialized witness coefficient | Witness object semantics and vertex numbering |
| Changed proof-data factor with independent expected result | Factor-position binding and cell reconstruction |

The synthetic controls prove that the independent primitives detect these mathematical failures once they receive explicit objects.
They do not prove that the compact input strings decode to those objects.
