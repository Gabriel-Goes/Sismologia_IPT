#!/usr/bin/env bash
set -euo pipefail

# Real run until final compatible events dataset (pre-RNC).
# Criteria (strict): inside MG polygon, mag<4, depth<10, year>=MIN_YEAR(last),
# P<=400km, window P-10/P+50, channels HHZ/HHN/HHE.

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  cat <<'EOF'
Usage:
  bash scripts/run_real_mg_maglt4_depthlt10.sh

Environment overrides:
  CLIENT_URL              (default: auto: seisapp->http://10.110.0.134, other->http://127.0.0.1:28080)
  SISBRA_CSV              (default: catalogs/sisbra/.../catalogo_CLEAN_v2024May09.csv)
  FILTERED_CSV            (default: outputs/sisbra_mg_maglt4_depthlt10.csv)
  STATE_FILTER            (default: MG, audit only for ST-vs-geometry)
  MIN_YEAR                (default: 2020, inclusive)
  STAGE_ROOT              (default: data/events_stage)
  NON_MATCHED_ROOT        (default: data/events_stage_non_matched)
  FINAL_ROOT              (default: data/events)
  WORKERS_STEP02          (default: 12)
  WORKERS_STEP03          (default: 12)
  MG_POLYGON_YEAR         (default: 2020)
  MG_GPKG_PATH            (default: ~/geodatabase.gpkg, from GeoServer rsync)
  MG_GPKG_LAYER           (default: ibge_mg_uf_2024)
  MAX_MAG                 (default: 4, strict '<')
  MAX_DEPTH_KM            (default: 10, strict '<')
  MAX_PICK_DIST_KM        (default: 400)
  PRE_P_S / POST_P_S      (default: 10 / 50)
  COMPONENT_CHANNELS      (default: HHZ,HHN,HHE)
  WAVEFORMS_SUBDIR        (default: waveform)
  STAGE_MUST_BE_EMPTY     (default: 1)
EOF
  exit 0
fi

HOSTNAME_FULL="$(hostname 2>/dev/null || true)"
HOSTNAME_LC="$(printf '%s' "$HOSTNAME_FULL" | tr '[:upper:]' '[:lower:]')"
DEFAULT_CLIENT_URL="http://127.0.0.1:28080"
if [[ "$HOSTNAME_LC" == *"seisapp"* ]]; then
  DEFAULT_CLIENT_URL="http://10.110.0.134"
fi
CLIENT_URL_SOURCE="auto"
if [ -n "${CLIENT_URL:-}" ]; then
  CLIENT_URL_SOURCE="env"
fi
CLIENT_URL="${CLIENT_URL:-$DEFAULT_CLIENT_URL}"
SISBRA_CSV="${SISBRA_CSV:-catalogs/sisbra/sisbra_v2024May09/catalogo_CLEAN_v2024May09.csv}"
FILTERED_CSV="${FILTERED_CSV:-outputs/sisbra_mg_maglt4_depthlt10.csv}"
STAGE_ROOT="${STAGE_ROOT:-data/events_stage}"
NON_MATCHED_ROOT="${NON_MATCHED_ROOT:-data/events_stage_non_matched}"
FINAL_ROOT="${FINAL_ROOT:-data/events}"
SUMMARY_CSV="${SUMMARY_CSV:-outputs/waveform_triplet_download_summary_events.csv}"
REPORT_CSV="${REPORT_CSV:-outputs/events_materialize_report.csv}"
REPORT_MD="${REPORT_MD:-outputs/events_materialize_report.md}"
NON_MATCHED_AUDIT_CSV="${NON_MATCHED_AUDIT_CSV:-outputs/non_matched_audit.csv}"
NON_MATCHED_AUDIT_MD="${NON_MATCHED_AUDIT_MD:-outputs/non_matched_audit.md}"
AMBIGUOUS_EVENTS_CSV="${AMBIGUOUS_EVENTS_CSV:-outputs/ambiguous_events.csv}"
NO_MATCH_EVENTS_CSV="${NO_MATCH_EVENTS_CSV:-outputs/no_match_events.csv}"
WORKERS_STEP02="${WORKERS_STEP02:-12}"
WORKERS_STEP03="${WORKERS_STEP03:-12}"
TIME_WINDOW_S="${TIME_WINDOW_S:-120}"
MAXRADIUS_DEG="${MAXRADIUS_DEG:-1.0}"
MAG_PAD="${MAG_PAD:-0.7}"
# Deprecated inclusion parameter: kept for ST-vs-geometry audit labels.
STATE_FILTER="${STATE_FILTER:-MG}"
MG_POLYGON_YEAR="${MG_POLYGON_YEAR:-2020}"
MG_GPKG_PATH="${MG_GPKG_PATH:-$HOME/geodatabase.gpkg}"
MG_GPKG_LAYER="${MG_GPKG_LAYER:-ibge_mg_uf_2024}"
MIN_YEAR="${MIN_YEAR:-2020}"
MAX_MAG="${MAX_MAG:-4}"
MAX_DEPTH_KM="${MAX_DEPTH_KM:-10}"
MAX_PICK_DIST_KM="${MAX_PICK_DIST_KM:-400}"
PRE_P_S="${PRE_P_S:-10}"
POST_P_S="${POST_P_S:-50}"
COMPONENT_CHANNELS="${COMPONENT_CHANNELS:-HHZ,HHN,HHE}"
WAVEFORMS_SUBDIR="${WAVEFORMS_SUBDIR:-waveform}"
STAGE_MUST_BE_EMPTY="${STAGE_MUST_BE_EMPTY:-1}"

LOG_DIR="${LOG_DIR:-outputs/logs_real_events}"
mkdir -p "$LOG_DIR"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="$LOG_DIR/run_real_mg_maglt4_depthlt10_${RUN_TS}.log"
REPORT_FILE="$LOG_DIR/run_real_mg_maglt4_depthlt10_${RUN_TS}.md"

if command -v pyenv >/dev/null 2>&1; then
  PYTHON_RUNNER=(pyenv exec python)
  PYTHON_DESC="pyenv exec python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_RUNNER=(python3)
  PYTHON_DESC="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_RUNNER=(python)
  PYTHON_DESC="python"
else
  echo "[run-real] ERROR: python interpreter not found (pyenv/python3/python)"
  exit 2
fi

if [ -d "$FINAL_ROOT" ] && [ -n "$(find "$FINAL_ROOT" -mindepth 1 -print -quit 2>/dev/null || true)" ]; then
  echo "[run-real] ERROR: $FINAL_ROOT is not empty."
  echo "[run-real] Clean it manually before running this flow."
  exit 1
fi

if [ "$STAGE_MUST_BE_EMPTY" = "1" ] && [ -d "$STAGE_ROOT" ] && [ -n "$(find "$STAGE_ROOT" -mindepth 1 -print -quit 2>/dev/null || true)" ]; then
  echo "[run-real] ERROR: $STAGE_ROOT is not empty and STAGE_MUST_BE_EMPTY=1."
  echo "[run-real] Clean it manually or set STAGE_MUST_BE_EMPTY=0."
  exit 1
fi
if [ "$STAGE_MUST_BE_EMPTY" = "1" ] && [ -d "$NON_MATCHED_ROOT" ] && [ -n "$(find "$NON_MATCHED_ROOT" -mindepth 1 -print -quit 2>/dev/null || true)" ]; then
  echo "[run-real] ERROR: $NON_MATCHED_ROOT is not empty and STAGE_MUST_BE_EMPTY=1."
  echo "[run-real] Clean it manually or set STAGE_MUST_BE_EMPTY=0."
  exit 1
fi

mkdir -p "$(dirname "$FILTERED_CSV")" "$STAGE_ROOT" "$NON_MATCHED_ROOT" "$FINAL_ROOT"

{
  echo "# Real Run Report ($RUN_TS)"
  echo
  echo "## Config"
  echo "- CLIENT_URL: \`$CLIENT_URL\`"
  echo "- CLIENT_URL_SOURCE: \`$CLIENT_URL_SOURCE\`"
  echo "- HOSTNAME: \`$HOSTNAME_FULL\`"
  echo "- SISBRA_CSV: \`$SISBRA_CSV\`"
  echo "- FILTERED_CSV: \`$FILTERED_CSV\`"
  echo "- STAGE_ROOT: \`$STAGE_ROOT\`"
  echo "- NON_MATCHED_ROOT: \`$NON_MATCHED_ROOT\`"
  echo "- FINAL_ROOT: \`$FINAL_ROOT\`"
  echo "- SUMMARY_CSV: \`$SUMMARY_CSV\`"
  echo "- STATE_FILTER (audit only): \`$STATE_FILTER\`"
  echo "- MG_POLYGON_YEAR: \`$MG_POLYGON_YEAR\`"
  echo "- MG_GPKG_PATH: \`$MG_GPKG_PATH\`"
  echo "- MG_GPKG_LAYER: \`$MG_GPKG_LAYER\`"
  echo "- MIN_YEAR (inclusive): \`>= $MIN_YEAR\`"
  echo "- MAX_MAG (strict): \`< $MAX_MAG\`"
  echo "- MAX_DEPTH_KM (strict): \`< $MAX_DEPTH_KM\`"
  echo "- MAX_PICK_DIST_KM: \`<= $MAX_PICK_DIST_KM\`"
  echo "- WINDOW: \`P-$PRE_P_S / P+$POST_P_S\`"
  echo "- COMPONENT_CHANNELS: \`$COMPONENT_CHANNELS\`"
  echo "- PYTHON_CMD: \`$PYTHON_DESC\`"
  echo
  echo "## Commands"
} > "$REPORT_FILE"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "[run-real] run_ts=$RUN_TS"
echo "[run-real] report=$REPORT_FILE"
echo "[run-real] log=$LOG_FILE"
echo "[run-real] python_cmd=$PYTHON_DESC"
echo "[run-real] python_exe=$(${PYTHON_RUNNER[@]} -c 'import sys; print(sys.executable)')"
echo "[run-real] endpoint_check via obspy client ..."
"${PYTHON_RUNNER[@]}" - "$CLIENT_URL" <<'PY'
import sys
from obspy.clients.fdsn import Client

url = sys.argv[1]
try:
    c = Client(url)
    v_event = c.get_webservice_version("event")
    v_station = c.get_webservice_version("station")
    v_data = c.get_webservice_version("dataselect")
    print(
        f"endpoint_check=ok client={url} "
        f"event_v={v_event} station_v={v_station} dataselect_v={v_data}"
    )
except Exception as e:
    print(f"endpoint_check=fail client={url} error={e}")
    raise
PY

echo "[run-real] step A: filter SISBRA"
cat >> "$REPORT_FILE" <<EOF

a) Filter SISBRA
\`\`\`bash
$PYTHON_DESC scripts/filter_sisbra_csv.py \\
  --input-csv "$SISBRA_CSV" \\
  --output-csv "$FILTERED_CSV" \\
  --state "$STATE_FILTER" \\
  --mg-polygon-year "$MG_POLYGON_YEAR" \\
  --mg-polygon-gpkg "$MG_GPKG_PATH" \\
  --mg-polygon-layer "$MG_GPKG_LAYER" \\
  --min-year "$MIN_YEAR" \\
  --max-mag "$MAX_MAG" \\
  --max-depth-km "$MAX_DEPTH_KM"
\`\`\`
EOF
"${PYTHON_RUNNER[@]}" scripts/filter_sisbra_csv.py \
  --input-csv "$SISBRA_CSV" \
  --output-csv "$FILTERED_CSV" \
  --state "$STATE_FILTER" \
  --mg-polygon-year "$MG_POLYGON_YEAR" \
  --mg-polygon-gpkg "$MG_GPKG_PATH" \
  --mg-polygon-layer "$MG_GPKG_LAYER" \
  --min-year "$MIN_YEAR" \
  --max-mag "$MAX_MAG" \
  --max-depth-km "$MAX_DEPTH_KM"

echo "[run-real] step B: step02"
cat >> "$REPORT_FILE" <<EOF

b) Step02
\`\`\`bash
$PYTHON_DESC src/seismic_event_discriminator/step02_fdsn_picks_export.py \\
  --sisbra-csv "$FILTERED_CSV" \\
  --client-url "$CLIENT_URL" \\
  --n-last 0 \\
  --workers "$WORKERS_STEP02" \\
  --out-root "$STAGE_ROOT" \\
  --non-matched-root "$NON_MATCHED_ROOT" \\
  --max-pick-dist-km "$MAX_PICK_DIST_KM" \\
  --time-window-s "$TIME_WINDOW_S" \\
  --maxradius-deg "$MAXRADIUS_DEG" \\
  --mag-pad "$MAG_PAD" \\
  --step03-output-mode triplet_single_file \\
  --step03-component-channels "$COMPONENT_CHANNELS"
\`\`\`
EOF
"${PYTHON_RUNNER[@]}" src/seismic_event_discriminator/step02_fdsn_picks_export.py \
  --sisbra-csv "$FILTERED_CSV" \
  --client-url "$CLIENT_URL" \
  --n-last 0 \
  --workers "$WORKERS_STEP02" \
  --out-root "$STAGE_ROOT" \
  --non-matched-root "$NON_MATCHED_ROOT" \
  --max-pick-dist-km "$MAX_PICK_DIST_KM" \
  --time-window-s "$TIME_WINDOW_S" \
  --maxradius-deg "$MAXRADIUS_DEG" \
  --mag-pad "$MAG_PAD" \
  --step03-output-mode triplet_single_file \
  --step03-component-channels "$COMPONENT_CHANNELS"

echo "[run-real] step B2: audit non-matched bundles"
cat >> "$REPORT_FILE" <<EOF

b2) Audit no_match + ambiguous
\`\`\`bash
$PYTHON_DESC scripts/audit_non_matched_events.py \\
  --non-matched-root "$NON_MATCHED_ROOT" \\
  --report-csv "$NON_MATCHED_AUDIT_CSV" \\
  --report-md "$NON_MATCHED_AUDIT_MD" \\
  --ambiguous-csv "$AMBIGUOUS_EVENTS_CSV" \\
  --no-match-csv "$NO_MATCH_EVENTS_CSV"
\`\`\`
EOF
if find "$NON_MATCHED_ROOT" -type f -name event.json -print -quit 2>/dev/null | grep -q .; then
  "${PYTHON_RUNNER[@]}" scripts/audit_non_matched_events.py \
    --non-matched-root "$NON_MATCHED_ROOT" \
    --report-csv "$NON_MATCHED_AUDIT_CSV" \
    --report-md "$NON_MATCHED_AUDIT_MD" \
    --ambiguous-csv "$AMBIGUOUS_EVENTS_CSV" \
    --no-match-csv "$NO_MATCH_EVENTS_CSV"
else
  echo "[run-real] no non-matched bundles found under $NON_MATCHED_ROOT; skipping audit"
fi

echo "[run-real] step C: step03"
cat >> "$REPORT_FILE" <<EOF

c) Step03
\`\`\`bash
$PYTHON_DESC scripts/step03_waveforms_from_p_picks.py \\
  --events-root "$STAGE_ROOT" \\
  --client-url "$CLIENT_URL" \\
  --max-pick-dist-km "$MAX_PICK_DIST_KM" \\
  --pre-p-s "$PRE_P_S" \\
  --post-p-s "$POST_P_S" \\
  --workers "$WORKERS_STEP03" \\
  --waveforms-subdir "$WAVEFORMS_SUBDIR" \\
  --summary-csv "$SUMMARY_CSV" \\
  --state-filter "$STATE_FILTER" \\
  --mg-polygon-year "$MG_POLYGON_YEAR" \\
  --mg-polygon-gpkg "$MG_GPKG_PATH" \\
  --mg-polygon-layer "$MG_GPKG_LAYER" \\
  --max-mag "$MAX_MAG" \\
  --max-depth-km "$MAX_DEPTH_KM" \\
  --min-year "$MIN_YEAR" \\
  --component-channels "$COMPONENT_CHANNELS"
\`\`\`
EOF
"${PYTHON_RUNNER[@]}" scripts/step03_waveforms_from_p_picks.py \
  --events-root "$STAGE_ROOT" \
  --client-url "$CLIENT_URL" \
  --max-pick-dist-km "$MAX_PICK_DIST_KM" \
  --pre-p-s "$PRE_P_S" \
  --post-p-s "$POST_P_S" \
  --workers "$WORKERS_STEP03" \
  --waveforms-subdir "$WAVEFORMS_SUBDIR" \
  --summary-csv "$SUMMARY_CSV" \
  --state-filter "$STATE_FILTER" \
  --mg-polygon-year "$MG_POLYGON_YEAR" \
  --mg-polygon-gpkg "$MG_GPKG_PATH" \
  --mg-polygon-layer "$MG_GPKG_LAYER" \
  --max-mag "$MAX_MAG" \
  --max-depth-km "$MAX_DEPTH_KM" \
  --min-year "$MIN_YEAR" \
  --component-channels "$COMPONENT_CHANNELS"

echo "[run-real] step D: materialize final dataset"
cat >> "$REPORT_FILE" <<EOF

d) Materialize final dataset
\`\`\`bash
$PYTHON_DESC scripts/materialize_events_dataset.py \\
  --events-root "$STAGE_ROOT" \\
  --download-summary-csv "$SUMMARY_CSV" \\
  --output-root "$FINAL_ROOT" \\
  --state-filter "$STATE_FILTER" \\
  --mg-polygon-year "$MG_POLYGON_YEAR" \\
  --mg-polygon-gpkg "$MG_GPKG_PATH" \\
  --mg-polygon-layer "$MG_GPKG_LAYER" \\
  --max-mag "$MAX_MAG" \\
  --max-depth-km "$MAX_DEPTH_KM" \\
  --min-year "$MIN_YEAR" \\
  --max-pick-dist-km "$MAX_PICK_DIST_KM" \\
  --datetime-source fdsn_then_sisbra \\
  --datetime-format %Y%jT%H%M%S \\
  --waveforms-subdir "$WAVEFORMS_SUBDIR" \\
  --collision-policy abort \\
  --report-csv "$REPORT_CSV" \\
  --report-md "$REPORT_MD"
\`\`\`
EOF
"${PYTHON_RUNNER[@]}" scripts/materialize_events_dataset.py \
  --events-root "$STAGE_ROOT" \
  --download-summary-csv "$SUMMARY_CSV" \
  --output-root "$FINAL_ROOT" \
  --state-filter "$STATE_FILTER" \
  --mg-polygon-year "$MG_POLYGON_YEAR" \
  --mg-polygon-gpkg "$MG_GPKG_PATH" \
  --mg-polygon-layer "$MG_GPKG_LAYER" \
  --max-mag "$MAX_MAG" \
  --max-depth-km "$MAX_DEPTH_KM" \
  --min-year "$MIN_YEAR" \
  --max-pick-dist-km "$MAX_PICK_DIST_KM" \
  --datetime-source fdsn_then_sisbra \
  --datetime-format %Y%jT%H%M%S \
  --waveforms-subdir "$WAVEFORMS_SUBDIR" \
  --collision-policy abort \
  --report-csv "$REPORT_CSV" \
  --report-md "$REPORT_MD"

{
  echo
  echo "## Outputs"
  echo "- Stage root: \`$STAGE_ROOT\`"
  echo "- Non-matched root: \`$NON_MATCHED_ROOT\`"
  echo "- Final root: \`$FINAL_ROOT\`"
  echo "- Non-matched audit CSV: \`$NON_MATCHED_AUDIT_CSV\`"
  echo "- Non-matched audit MD: \`$NON_MATCHED_AUDIT_MD\`"
  echo "- Ambiguous events CSV: \`$AMBIGUOUS_EVENTS_CSV\`"
  echo "- No-match events CSV: \`$NO_MATCH_EVENTS_CSV\`"
  echo "- Waveform summary: \`$SUMMARY_CSV\`"
  echo "- Materialize report CSV: \`$REPORT_CSV\`"
  echo "- Materialize report MD: \`$REPORT_MD\`"
  echo "- Log file: \`$LOG_FILE\`"
} >> "$REPORT_FILE"

echo "[run-real] done"
echo "[run-real] report=$REPORT_FILE"
echo "[run-real] log=$LOG_FILE"
