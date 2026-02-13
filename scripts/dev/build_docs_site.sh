#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

NEW_SRC="$ROOT_DIR/docs/sphinx/source"

OUT_ROOT="$ROOT_DIR/docs/site"

mkdir -p "$OUT_ROOT"

echo "[docs] Building main docs Alpha -> $OUT_ROOT"
sphinx-build -b html "$NEW_SRC" "$OUT_ROOT"

if [[ "${BUILD_LEGACY:-0}" == "1" ]]; then
  LEGACY_SRC="$ROOT_DIR/docs/legacy_snapshot/sphinx_source"
  OUT_LEGACY="$OUT_ROOT/legado"
  mkdir -p "$OUT_LEGACY"
  echo "[docs] Building legacy snapshot -> $OUT_LEGACY"
  sphinx-build -b html "$LEGACY_SRC" "$OUT_LEGACY"
else
  echo "[docs] Skipping legacy snapshot build (set BUILD_LEGACY=1 to enable)."
fi

echo "[docs] Done."
echo "[docs] Open: file://$OUT_ROOT/index.html"
