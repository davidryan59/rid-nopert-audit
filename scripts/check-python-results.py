#!/usr/bin/env python3
"""Validate the complete Python checker output without version-sensitive bytes."""

import json
import sys
from collections import Counter
from pathlib import Path


EXPECTED_COMPONENTS = {
    "Domain": 12_650,
    "Global": 157_458,
    "Local": 21_792,
    "Exotic": 796,
}
EXPECTED_RECORDS = 192_696


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check-python-results.py RESULTS.jsonl")

    path = Path(sys.argv[1])
    records = []
    with path.open(encoding="utf-8") as source:
        for number, line in enumerate(source, start=1):
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise SystemExit(f"invalid JSON on output line {number}: {error}")

    if len(records) != EXPECTED_RECORDS:
        raise SystemExit(f"expected {EXPECTED_RECORDS} records, found {len(records)}")

    refused = [record for record in records if record.get("ok") is not True]
    if refused:
        raise SystemExit(f"Python checker refused {len(refused)} records")

    source_lines = [record.get("line") for record in records]
    if len(set(source_lines)) != EXPECTED_RECORDS:
        raise SystemExit("source line numbers are incomplete or duplicated")
    if min(source_lines) != 2 or max(source_lines) != EXPECTED_RECORDS + 1:
        raise SystemExit("source line numbers do not cover the full certificate")

    components = Counter(record.get("component") for record in records)
    if dict(components) != EXPECTED_COMPONENTS:
        raise SystemExit(f"unexpected component counts: {dict(components)}")

    print(f"Validated {EXPECTED_RECORDS} accepted Python results")
    print(f"Component counts: {dict(components)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
