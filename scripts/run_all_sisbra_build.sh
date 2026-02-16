#!/usr/bin/env bash
set -euo pipefail

# Full run: process all SISBRA events and build event bundles.
# It also records endpoint connectivity checks for reporting.

CLIENT_URL="${CLIENT_URL:-http://127.0.0.1:28080}"
UNB_WADL_URL="${UNB_WADL_URL:-http://164.41.28.122:5831/fdsnws/event/1/application.wadl}"
SISBRA_CSV="${SISBRA_CSV:-catalogs/sisbra/sisbra_v2024May09/catalogo_CLEAN_v2024May09.csv}"
OUT_ROOT="${OUT_ROOT:-data/sisbra_all}"
N_LAST="${N_LAST:-0}"
WORKERS="${WORKERS:-1}"
MAX_PICK_DIST_KM="${MAX_PICK_DIST_KM:-400}"
TIME_WINDOW_S="${TIME_WINDOW_S:-120}"
MAXRADIUS_DEG="${MAXRADIUS_DEG:-1.0}"
MAG_PAD="${MAG_PAD:-0.7}"
LOG_DIR="${LOG_DIR:-outputs/logs}"

mkdir -p "$LOG_DIR"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="$LOG_DIR/run_all_sisbra_${RUN_TS}.log"
REPORT_FILE="$LOG_DIR/run_all_sisbra_${RUN_TS}.md"
SUMMARY_CSV="$LOG_DIR/run_all_sisbra_${RUN_TS}_summary.csv"

PYENV_OK="no"
if command -v pyenv >/dev/null 2>&1; then
  PYENV_OK="yes"
  PYTHON_RUNNER=(pyenv exec python)
  PYTHON_DESC="pyenv exec python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_RUNNER=(python3)
  PYTHON_DESC="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_RUNNER=(python)
  PYTHON_DESC="python"
else
  {
    echo "# SISBRA Full Run Report ($RUN_TS)"
    echo
    echo "## Exit"
    echo "- error: \`python interpreter not found (pyenv/python3/python)\`"
  } >"$REPORT_FILE"
  echo "[run-all] error: python interpreter not found (pyenv/python3/python)"
  echo "[run-all] report: $REPORT_FILE"
  exit 2
fi

PYTHON_EXE="$("${PYTHON_RUNNER[@]}" -c 'import sys; print(sys.executable)' 2>/dev/null || true)"
OBSPY_VER="$("${PYTHON_RUNNER[@]}" -c 'import obspy; print(obspy.__version__)' 2>/dev/null || true)"

echo "[run-all] run_ts=$RUN_TS"
echo "[run-all] report=$REPORT_FILE"
echo "[run-all] log=$LOG_FILE"
echo "[run-all] summary_csv=$SUMMARY_CSV"

{
  echo "# SISBRA Full Run Report ($RUN_TS)"
  echo
  echo "## Config"
  echo "- CLIENT_URL: \`$CLIENT_URL\`"
  echo "- UNB_WADL_URL: \`$UNB_WADL_URL\`"
  echo "- SISBRA_CSV: \`$SISBRA_CSV\`"
  echo "- OUT_ROOT: \`$OUT_ROOT\`"
  echo "- N_LAST: \`$N_LAST\`"
  echo "- WORKERS: \`$WORKERS\`"
  echo "- MAX_PICK_DIST_KM: \`$MAX_PICK_DIST_KM\`"
  echo "- TIME_WINDOW_S: \`$TIME_WINDOW_S\`"
  echo "- MAXRADIUS_DEG: \`$MAXRADIUS_DEG\`"
  echo "- MAG_PAD: \`$MAG_PAD\`"
  echo "- PYTHON_CMD: \`$PYTHON_DESC\`"
  echo
  echo "## Endpoint Checks"
} >"$REPORT_FILE"

{
  echo "- pyenv available: \`$PYENV_OK\`"
  if [ "$PYENV_OK" = "yes" ]; then
    echo "- pyenv version: \`$(pyenv --version)\`"
    echo "- pyenv env: \`$(pyenv version-name 2>/dev/null || true)\`"
  fi
  echo "- python exe: \`${PYTHON_EXE:-unavailable}\`"
  echo "- obspy: \`${OBSPY_VER:-unavailable}\`"
} >>"$REPORT_FILE"

SEISARC_CHECK="fail"
SEISARC_ERR=""
if curl -fsS --max-time 10 "$CLIENT_URL/fdsnws/event/1/application.wadl" >/dev/null 2>&1; then
  SEISARC_CHECK="ok"
else
  SEISARC_ERR="$(curl -sS --max-time 10 "$CLIENT_URL/fdsnws/event/1/application.wadl" 2>&1 || true)"
fi

UNB_CHECK="fail"
UNB_ERR=""
if curl -fsS --max-time 10 "$UNB_WADL_URL" >/dev/null 2>&1; then
  UNB_CHECK="ok"
else
  UNB_ERR="$(curl -sS --max-time 10 "$UNB_WADL_URL" 2>&1 || true)"
fi

{
  echo "- seisArc WADL check: \`$SEISARC_CHECK\`"
  if [ -n "$SEISARC_ERR" ]; then
    echo "  - error: \`$SEISARC_ERR\`"
  fi
  echo "- UnB WADL check: \`$UNB_CHECK\`"
  if [ -n "$UNB_ERR" ]; then
    echo "  - error: \`$UNB_ERR\`"
  fi
  echo
  echo "## Run Command"
  echo '```bash'
  echo "$PYTHON_DESC src/seismic_event_discriminator/step02_fdsn_picks_export.py \\"
  echo "  --sisbra-csv \"$SISBRA_CSV\" \\"
  echo "  --client-url \"$CLIENT_URL\" \\"
  echo "  --n-last \"$N_LAST\" \\"
  echo "  --workers \"$WORKERS\" \\"
  echo "  --out-root \"$OUT_ROOT\" \\"
  echo "  --max-pick-dist-km \"$MAX_PICK_DIST_KM\" \\"
  echo "  --time-window-s \"$TIME_WINDOW_S\" \\"
  echo "  --maxradius-deg \"$MAXRADIUS_DEG\" \\"
  echo "  --mag-pad \"$MAG_PAD\""
  echo '```'
  echo
} >>"$REPORT_FILE"

echo "[run-all] starting step02 full run ..."

CMD=(
  "${PYTHON_RUNNER[@]}" src/seismic_event_discriminator/step02_fdsn_picks_export.py
  --sisbra-csv "$SISBRA_CSV"
  --client-url "$CLIENT_URL"
  --n-last "$N_LAST"
  --workers "$WORKERS"
  --out-root "$OUT_ROOT"
  --max-pick-dist-km "$MAX_PICK_DIST_KM"
  --time-window-s "$TIME_WINDOW_S"
  --maxradius-deg "$MAXRADIUS_DEG"
  --mag-pad "$MAG_PAD"
)

set +e
"${CMD[@]}" 2>&1 | tee "$LOG_FILE"
RUN_RC="${PIPESTATUS[0]}"
set -e
echo "[run-all] step02 rc=$RUN_RC"

"${PYTHON_RUNNER[@]}" - "$OUT_ROOT" "$SUMMARY_CSV" "$REPORT_FILE" <<'PY'
import csv
import glob
import json
import os
import sys
from collections import Counter

out_root, summary_csv, report_file = sys.argv[1], sys.argv[2], sys.argv[3]
paths = sorted(glob.glob(os.path.join(out_root, "*", "event.json")))
rows = []
counts = Counter()
for p in paths:
    try:
        d = json.load(open(p, "r", encoding="utf-8"))
    except Exception:
        continue
    status = d.get("match_status", "")
    counts[status] += 1
    sis = d.get("sisbra") or {}
    fdsn = d.get("fdsn") or {}
    rows.append(
        {
            "folder": os.path.basename(os.path.dirname(p)),
            "match_status": status,
            "sisbra_time": sis.get("origin_time", ""),
            "sisbra_lat": sis.get("latitude", ""),
            "sisbra_lon": sis.get("longitude", ""),
            "sisbra_mag": sis.get("magnitude", ""),
            "fdsn_event_id": (fdsn.get("resource_id", "").split("/")[-1] if fdsn.get("resource_id") else ""),
            "fdsn_origin_time": fdsn.get("origin_time", ""),
            "picks_count": len(d.get("picks") or []),
        }
    )

os.makedirs(os.path.dirname(summary_csv) or ".", exist_ok=True)
if rows:
    with open(summary_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

with open(report_file, "a", encoding="utf-8") as f:
    f.write("## Output Summary\n")
    f.write(f"- event bundles found: `{len(rows)}`\n")
    f.write(f"- summary csv: `{summary_csv}`\n")
    f.write("- status counts:\n")
    for k in sorted(counts):
        f.write(f"  - `{k}`: `{counts[k]}`\n")
    f.write("\n")
PY

{
  echo "## Exit"
  echo "- step02 rc: \`$RUN_RC\`"
  echo "- log: \`$LOG_FILE\`"
} >>"$REPORT_FILE"

echo "[run-all] done. rc=$RUN_RC"
echo "[run-all] report: $REPORT_FILE"
echo "[run-all] log:    $LOG_FILE"
echo "[run-all] summary:$SUMMARY_CSV"
exit "$RUN_RC"
