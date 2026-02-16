#!/usr/bin/env bash
set -euo pipefail

# Quick parallel smoke test tuned for SEISAPP.
# It runs a limited subset first, to validate parallel settings before full batch.

if ! command -v nproc >/dev/null 2>&1; then
  CPU=8
else
  CPU="$(nproc)"
fi

# Conservative default: half cores, capped at 24.
HALF=$(( CPU / 2 ))
if [ "$HALF" -lt 1 ]; then
  HALF=1
fi
if [ "$HALF" -gt 24 ]; then
  HALF=24
fi

WORKERS="${WORKERS:-$HALF}"
N_LAST="${N_LAST:-300}"
OUT_ROOT="${OUT_ROOT:-data/sisbra_parallel_smoketest}"
CLIENT_URL="${CLIENT_URL:-http://seisarc.sismo.iag.usp.br}"

echo "[parallel-smoke] cpu=$CPU workers=$WORKERS n_last=$N_LAST out_root=$OUT_ROOT"

WORKERS="$WORKERS" \
N_LAST="$N_LAST" \
OUT_ROOT="$OUT_ROOT" \
CLIENT_URL="$CLIENT_URL" \
bash scripts/run_all_sisbra_build.sh
