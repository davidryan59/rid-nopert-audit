#!/bin/sh
# SPDX-License-Identifier: MIT

set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
SOURCE="$ROOT/report/audit-report.md"
HTML="$ROOT/report/audit-report.html"
PDF="$ROOT/report/audit-report.pdf"
CSS="$ROOT/report/report.css"

if ! command -v pandoc >/dev/null 2>&1; then
    echo "Pandoc is required." >&2
    exit 2
fi

CHROME=""
for candidate in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium" \
    "/usr/bin/google-chrome" \
    "/usr/bin/chromium" \
    "/usr/bin/chromium-browser"
do
    if [ -x "$candidate" ]; then
        CHROME=$candidate
        break
    fi
done

if [ -z "$CHROME" ]; then
    echo "Chrome or Chromium is required." >&2
    exit 2
fi

pandoc "$SOURCE" \
    --from=gfm \
    --to=html5 \
    --standalone \
    --embed-resources \
    --css="$CSS" \
    --metadata pagetitle="Independent Audit of the Nopert Certificate for the Rhombicosidodecahedron" \
    --output="$HTML"

"$CHROME" \
    --headless \
    --disable-gpu \
    --no-pdf-header-footer \
    --print-to-pdf="$PDF" \
    "file://$HTML"

echo "Built $PDF"
