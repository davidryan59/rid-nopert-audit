# Clean-room run record

## Summary

The independent checker accepted all 38 required `rid-cover/1` files. It used exact arithmetic in `Q(sqrt(5))` throughout.

## Integrity checks

The specification check ran before implementation.

```text
shasum -a 256 /Users/davidryan/code/projects/rid-nopert-audit/specification/SHA256SUMS
shasum -a 256 -c SHA256SUMS
```

The first command returned:

```text
5f0f6e67a0ba7cf121750aa1ef4f09b86896303adcda467e2216b7f918e5296f
```

The second command returned `OK` for all six files listed by `SHA256SUMS`. `VERSION.json` identified `rid-cover/1-spec.1` and repeated that digest.

After the full run, this command rechecked all 47 permitted files:

```text
shasum -a 256 -c INPUT-MANIFEST.sha256
```

It returned `OK` for eight specification files, the article, and all 38 cover files.

## Environment

```text
Python 3.8.13
Darwin 25.6.0 arm64
```

The implementation uses Python's standard library. It uses no external package, network service, numerical approximation, or tolerance.

## Tests

The final test command was:

```text
python3 -m unittest -v test_checker.py
```

All 13 tests passed. The suite has seven arithmetic, grammar, and specification tests, plus six fail-closed mutation tests.

```text
Ran 13 tests in 0.256s
OK
real 0.56
user 0.32
sys 0.04
```

The mutations changed cover identity, zoom count, tree grammar, factor support, delegation placement, and witness range. Each mutation was rejected.

## Complete run

The exact command was:

```text
python3 checker.py --all --output RESULT-MANIFEST.json
```

The command returned exit status zero. The manifest reports 1,437.573459 seconds for the complete run.

The checker validated 11,231 leaves. Of these, 11,183 used witnesses and 48 used delegated hand-over.

It performed 357,856 corner evaluations and checked 1,260,757 exact Bernstein coefficients.

| File | Result | Seconds | Leaves | Delegated | Bernstein coefficients |
|---|---:|---:|---:|---:|---:|
| `exotic/arc+.json` | pass | 42.992472 | 343 | 0 | 46,020 |
| `exotic/arc-.json` | pass | 29.333906 | 288 | 0 | 30,466 |
| `exotic/crossing+.json` | pass | 213.111321 | 1,465 | 34 | 231,795 |
| `exotic/crossing-.json` | pass | 77.984648 | 701 | 14 | 90,802 |
| `exotic/endpoint+.json` | pass | 43.863451 | 305 | 0 | 51,409 |
| `exotic/endpoint-.json` | pass | 29.298465 | 246 | 0 | 36,256 |
| `exotic/pentagon.json` | pass | 814.910696 | 6,173 | 0 | 629,568 |
| `exotic/square.json` | pass | 94.710493 | 877 | 0 | 85,113 |
| `local/0.json` | pass | 2.543108 | 24 | 0 | 1,728 |
| `local/1.json` | pass | 4.766524 | 45 | 0 | 3,240 |
| `local/10.json` | pass | 1.616523 | 15 | 0 | 1,080 |
| `local/11.json` | pass | 1.321792 | 12 | 0 | 864 |
| `local/12.json` | pass | 5.484773 | 49 | 0 | 3,528 |
| `local/13.json` | pass | 1.296437 | 12 | 0 | 864 |
| `local/14.json` | pass | 4.999645 | 45 | 0 | 3,240 |
| `local/15.json` | pass | 1.622532 | 15 | 0 | 1,080 |
| `local/16.json` | pass | 4.232317 | 39 | 0 | 2,736 |
| `local/17.json` | pass | 2.414354 | 22 | 0 | 1,584 |
| `local/18.json` | pass | 2.045846 | 19 | 0 | 1,368 |
| `local/19.json` | pass | 7.657433 | 67 | 0 | 4,860 |
| `local/2.json` | pass | 2.790685 | 26 | 0 | 1,872 |
| `local/20.json` | pass | 1.849410 | 17 | 0 | 1,224 |
| `local/21.json` | pass | 2.705394 | 25 | 0 | 1,800 |
| `local/22.json` | pass | 3.357919 | 31 | 0 | 2,232 |
| `local/23.json` | pass | 3.804872 | 35 | 0 | 2,520 |
| `local/24.json` | pass | 1.839699 | 17 | 0 | 1,224 |
| `local/25.json` | pass | 3.188246 | 29 | 0 | 2,088 |
| `local/26.json` | pass | 2.030737 | 19 | 0 | 1,296 |
| `local/27.json` | pass | 1.834504 | 17 | 0 | 1,224 |
| `local/28.json` | pass | 1.149253 | 11 | 0 | 720 |
| `local/29.json` | pass | 9.390274 | 85 | 0 | 5,652 |
| `local/3.json` | pass | 3.031390 | 27 | 0 | 1,944 |
| `local/4.json` | pass | 1.757372 | 16 | 0 | 1,152 |
| `local/5.json` | pass | 2.198878 | 20 | 0 | 1,440 |
| `local/6.json` | pass | 1.967237 | 18 | 0 | 1,296 |
| `local/7.json` | pass | 2.988730 | 27 | 0 | 1,944 |
| `local/8.json` | pass | 1.665529 | 15 | 0 | 1,080 |
| `local/9.json` | pass | 3.690619 | 34 | 0 | 2,448 |

## Frozen hashes

`SOURCE-MANIFEST.sha256` defines the implementation tree as `BOUNDARY.md`, `README.md`, `checker.py`, and `test_checker.py`.

```text
3d8cca95ce326b8835104171fe0ed16d67d5b5895767b5ddd424546ba085abc7  SOURCE-MANIFEST.sha256
f9791caaf628ff79d6c9b6a680cca1aefeec748d6d7c154a51322ed65371c8b4  RESULT-MANIFEST.json
3e7361ad7567d40cc2eb561b5e7a28014acbb65e68b284a246b65d85090bf8c3  INPUT-MANIFEST.sha256
```
