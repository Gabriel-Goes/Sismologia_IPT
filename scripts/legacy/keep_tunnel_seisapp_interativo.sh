#!/usr/bin/env bash
set -u

REMOTE_USER="ggrl"
REMOTE_HOST="geodb.duckdns.org"
REMOTE_SSH_PORT="62222"

FORWARDS=(
  "127.0.0.1:22022:127.0.0.1:22"
  "127.0.0.1:28080:10.110.0.134:80"
  "127.0.0.1:28443:10.110.0.134:443"
)

MAX_CONSEC_FAILS=0
MIN_STABLE_SECONDS=120
SLEEP_BETWEEN_RETRIES=10

fails=0

while true; do
  start_ts=$(date +%s)
  echo "[tunnel] starting at $(date) (fails=$fails)"

  cmd=(
    ssh -N -T
    -p "$REMOTE_SSH_PORT"
    -o ExitOnForwardFailure=yes
    -o ServerAliveInterval=30
    -o ServerAliveCountMax=3
  )

  for fwd in "${FORWARDS[@]}"; do
    cmd+=(-R "$fwd")
  done

  cmd+=("${REMOTE_USER}@${REMOTE_HOST}")
  "${cmd[@]}"

  rc=$?
  end_ts=$(date +%s)
  runtime=$((end_ts - start_ts))

  echo "[tunnel] exited rc=$rc after ${runtime}s at $(date)"

  if [ "$runtime" -ge "$MIN_STABLE_SECONDS" ]; then
    fails=0
  else
    fails=$((fails + 1))
  fi

  if [ "$MAX_CONSEC_FAILS" -gt 0 ] && [ "$fails" -ge "$MAX_CONSEC_FAILS" ]; then
    echo "[tunnel] stopping after $fails consecutive quick failures"
    exit 1
  fi

  sleep "$SLEEP_BETWEEN_RETRIES"
done
