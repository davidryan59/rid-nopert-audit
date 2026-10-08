#!/bin/sh
# SPDX-License-Identifier: MIT

set -eu

REPOSITORY=https://github.com/bence-hervay/nopert-rid.git
COMMIT=802a3ded09535c4a99cef1371ce0d0277c433fa8
AUDIT_ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
WORK=${1:-work}
case "$WORK" in
    /*) ;;
    *) WORK="$(pwd)/$WORK" ;;
esac
SOURCE="$WORK/nopert-rid"
LOGS="$WORK/logs"

if [ -e "$WORK" ]; then
    echo "Refusing to overwrite existing path: $WORK" >&2
    echo "Pass a new working directory as the first argument." >&2
    exit 2
fi

for program in git cargo python3 uv awk cmp; do
    if ! command -v "$program" >/dev/null 2>&1; then
        echo "Required program is missing: $program" >&2
        exit 2
    fi
done

if command -v sha256sum >/dev/null 2>&1; then
    SHA256="sha256sum"
elif command -v shasum >/dev/null 2>&1; then
    SHA256="shasum -a 256"
else
    echo "Required SHA-256 program is missing." >&2
    exit 2
fi

mkdir -p "$LOGS"

run() {
    name=$1
    shift
    echo "+ $*"
    status=0
    "$@" > "$LOGS/$name.log" 2>&1 || status=$?
    cat "$LOGS/$name.log"
    return "$status"
}

run clone git clone "$REPOSITORY" "$SOURCE"
run checkout git -C "$SOURCE" checkout --detach "$COMMIT"

actual_commit=$(git -C "$SOURCE" rev-parse HEAD)
if [ "$actual_commit" != "$COMMIT" ]; then
    echo "Unexpected commit: $actual_commit" >&2
    exit 1
fi

verify_hash() {
    expected=$1
    relative=$2
    actual=$(cd "$SOURCE" && $SHA256 "$relative" | awk '{print $1}')
    if [ "$actual" != "$expected" ]; then
        echo "Hash mismatch for $relative" >&2
        echo "Expected $expected" >&2
        echo "Actual   $actual" >&2
        exit 1
    fi
    printf '%s  %s\n' "$actual" "$relative" >> "$LOGS/input-hashes.sha256"
}

verify_hash e52022737fad1f5add102b8a8b357788a3c5086111f028255a6e7a26d6bd71ff paper/article.pdf
verify_hash 2f40f55632dcbccd722fcd2681153f1f5472984680680d3346dbcee4dbb1bd24 proof/Cargo.lock
verify_hash bc3024472c4f15317c4af96a26d299453b9d58c2d8875ad53b0dcece5de467af proof/results/full/check.json
verify_hash fe27092d65b3dd0907357318a5d42f1a5cfb11bdc89cff00ab153202df335f6f proof/results/full/search.json
verify_hash df1f8dbab68b561f22fa9daeca48153d71bde7b6fba3345d9f6b7b8077df4b5f proof/results/full/search.cert
verify_hash 2ea8eda0baf9f33ef03a0a8c946860b2f3def1eaffe154ba27d22f9b4f4bc44b audit/uv.lock

(cd "$SOURCE/proof" && run build cargo build --release --locked)
(cd "$SOURCE/proof" && run rust-check target/release/rid check results/full/check.json)

(cd "$SOURCE/audit" && run python-selftest uv run --frozen python selftest.py)
(cd "$SOURCE/audit" && run python-replay uv run --frozen python runall.py)
(cd "$SOURCE/audit" && run python-structure uv run --frozen python structure.py)
(cd "$SOURCE/audit" && run python-controls uv run --frozen python controls.py)

run python-result-check python3 "$AUDIT_ROOT/scripts/check-python-results.py" \
    "$SOURCE/audit/results.jsonl"
(cd "$SOURCE" && $SHA256 audit/results.jsonl) > "$LOGS/python-results.sha256"

(cd "$SOURCE/proof" && run rust-lib-tests cargo test --release --lib -- \
    --skip a_failed_write_poisons_the_store_and_leaves_a_recoverable_file \
    --skip timed_boxes_keep_every_worker_busy_and_commit_the_reference)

for test in command components floating_point interruption; do
    (cd "$SOURCE/proof" && run "rust-$test-tests" cargo test --release --test "$test")
done

(cd "$SOURCE/proof" && run zoom-model cargo test --release --lib \
    proof::tests::independent_verification_of_every_cell -- \
    --ignored --test-threads=4 --nocapture)

(cd "$SOURCE/proof" && run clean-search target/release/rid search examples/search.json)
if ! cmp -s "$SOURCE/proof/rid.cert" "$SOURCE/proof/results/full/search.cert"; then
    echo "Regenerated certificate differs from the supplied certificate." >&2
    exit 1
fi

$SHA256 "$SOURCE/proof/rid.cert" > "$LOGS/regenerated-certificate.sha256"

printf '%s\n' \
    "Outcome: reproduction passed" \
    "Commit: $COMMIT" \
    "Certificate: byte-identical" \
    "Certificate SHA-256: df1f8dbab68b561f22fa9daeca48153d71bde7b6fba3345d9f6b7b8077df4b5f" \
    > "$LOGS/result.txt"

echo "Reproduction passed. Logs: $LOGS"
