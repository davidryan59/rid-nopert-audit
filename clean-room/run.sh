#!/bin/zsh
set -euo pipefail

SCRIPT_PATH=$0
ROOT=$(cd "$(dirname "$SCRIPT_PATH")" && pwd)
cd "$ROOT"

export PYTHONNOUSERSITE=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/src"
export LC_ALL=C

{
    echo "command: $ROOT/run.sh"
    echo "started_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    python3 --version
    python3 -m unittest discover -s tests -v
    python3 src/checker.py \
        --inputs inputs \
        --output results/clean-room-result.json
    SOURCE_FILES=(
        README.md
        SPECIFICATION.md
        MUTATION-CONTROLS.md
        requirements.txt
        run.sh
        src/*.py
        tests/*.py
    )
    shasum -a 256 "${SOURCE_FILES[@]}" > results/source-hashes.sha256
    SOURCE_TREE_SHA=$(shasum -a 256 results/source-hashes.sha256 | awk '{print $1}')
    echo "source_tree_sha256: $SOURCE_TREE_SHA"
    echo "finished_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} 2>&1 | tee "$ROOT/results/run.log"
