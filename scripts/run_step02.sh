#!/usr/bin/env bash
set -euo pipefail

# Minimal runner to avoid long copy/paste commands in the terminal.
#
# Usage:
#   bash scripts/run_step02.sh
#
# Optional env vars:
#   CLIENT_URL=http://127.0.0.1:28080
#   SISBRA_CSV=...
#   N_LAST=3
#   OUT_ROOT=data_test_run
#   MAX_PICK_DIST_KM=400
#   TIME_WINDOW_S=120
#   MAXRADIUS_DEG=1.0
#   MAG_PAD=0.7

CLIENT_URL="${CLIENT_URL:-http://127.0.0.1:28080}"
SISBRA_CSV="${SISBRA_CSV:-catalogs/sisbra/sisbra_v2024May09/catalogo_CLEAN_v2024May09.csv}"
N_LAST="${N_LAST:-3}"
OUT_ROOT="${OUT_ROOT:-data_test_run}"
MAX_PICK_DIST_KM="${MAX_PICK_DIST_KM:-400}"
TIME_WINDOW_S="${TIME_WINDOW_S:-120}"
MAXRADIUS_DEG="${MAXRADIUS_DEG:-1.0}"
MAG_PAD="${MAG_PAD:-0.7}"

echo "[run_step02] repo: $(pwd)"
echo "[run_step02] CLIENT_URL=$CLIENT_URL"
echo "[run_step02] SISBRA_CSV=$SISBRA_CSV"
echo "[run_step02] N_LAST=$N_LAST OUT_ROOT=$OUT_ROOT MAX_PICK_DIST_KM=$MAX_PICK_DIST_KM"
echo

if command -v pyenv >/dev/null 2>&1; then
  PYTHON_RUNNER=(pyenv exec python)
  PYTHON_DESC="pyenv exec python"
  echo "[run_step02] pyenv: $(pyenv --version)"
  echo "[run_step02] pyenv version: $(pyenv version-name 2>/dev/null || true)"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_RUNNER=(python3)
  PYTHON_DESC="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_RUNNER=(python)
  PYTHON_DESC="python"
else
  echo "[run_step02] ERROR: python interpreter not found (pyenv/python3/python)"
  exit 2
fi

echo "[run_step02] python_cmd: $PYTHON_DESC"
echo "[run_step02] python: $("${PYTHON_RUNNER[@]}" -c 'import sys; print(sys.executable)')"
"${PYTHON_RUNNER[@]}" -c "import obspy; print('[run_step02] obspy', obspy.__version__)"

echo
echo "[run_step02] checking FDSN endpoint (tunnel) ..."
curl -fsS --max-time 5 "${CLIENT_URL}/fdsnws/event/1/application.wadl" | head -n 3 | sed 's/^/[run_step02] wadl: /'

echo
echo "[run_step02] running step02 export ..."
rm -rf "$OUT_ROOT"
"${PYTHON_RUNNER[@]}" src/seismic_event_discriminator/step02_fdsn_picks_export.py \
  --sisbra-csv "$SISBRA_CSV" \
  --client-url "$CLIENT_URL" \
  --n-last "$N_LAST" \
  --out-root "$OUT_ROOT" \
  --max-pick-dist-km "$MAX_PICK_DIST_KM" \
  --time-window-s "$TIME_WINDOW_S" \
  --maxradius-deg "$MAXRADIUS_DEG" \
  --mag-pad "$MAG_PAD"

echo
echo "[run_step02] outputs:"
find "$OUT_ROOT" -maxdepth 2 -type f -name event.json -o -name event.xml | sort | sed 's/^/[run_step02]  /'

echo
echo "[run_step02] quick summary:"
"${PYTHON_RUNNER[@]}" - <<PY
import glob, json, os
out_root = ${OUT_ROOT!r}
paths = sorted(glob.glob(os.path.join(out_root, "*", "event.json")))
print("bundles:", len(paths))
for p in paths[:5]:
  d = json.load(open(p, "r", encoding="utf-8"))
  fdsn = (d.get("fdsn") or {}).get("resource_id")
  print("-", p, "status=", d.get("match_status"), "picks=", len(d.get("picks") or []), "fdsn=", fdsn)
PY
