#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CORE_REQ="$ROOT_DIR/scripts/dev/requirements-core-pipeline.txt"
RNC_REQ="$ROOT_DIR/scripts/dev/requirements-rnc-inference.txt"

ENV_NAME=""
PY_VER="3.12.11"
WITH_RNC="no"
SET_LOCAL="no"
CHECK_ONLY="no"

usage() {
  cat <<'USAGE'
Usage:
  scripts/dev/setup_pyenv_project.sh [options]

Options:
  --env NAME        pyenv virtualenv name (default: value from .python-version)
  --python VERSION  base python version for pyenv virtualenv creation (default: 3.12.11)
  --with-rnc        also install RNC inference deps (tensorflow)
  --set-local       run "pyenv local <env>" in repository root
  --check-only      only run diagnostics, do not create/install
  -h, --help        show this help

Examples:
  scripts/dev/setup_pyenv_project.sh --env geo-seis --python 3.12.11 --set-local
  scripts/dev/setup_pyenv_project.sh --env geo-seis-rnc --python 3.11.9 --with-rnc
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_NAME="${2:-}"
      shift 2
      ;;
    --python)
      PY_VER="${2:-}"
      shift 2
      ;;
    --with-rnc)
      WITH_RNC="yes"
      shift
      ;;
    --set-local)
      SET_LOCAL="yes"
      shift
      ;;
    --check-only)
      CHECK_ONLY="yes"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[pyenv-setup] unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if ! command -v pyenv >/dev/null 2>&1; then
  echo "[pyenv-setup] pyenv not found in PATH." >&2
  echo "[pyenv-setup] Install pyenv first or use plain python3 on hosts without pyenv." >&2
  exit 2
fi

if [[ -z "$ENV_NAME" ]] && [[ -f "$ROOT_DIR/.python-version" ]]; then
  ENV_NAME="$(head -n1 "$ROOT_DIR/.python-version" | tr -d '[:space:]')"
fi
if [[ -z "$ENV_NAME" ]]; then
  echo "[pyenv-setup] could not determine env name. Use --env NAME." >&2
  exit 2
fi

if ! pyenv commands | grep -q '^virtualenv$'; then
  echo "[pyenv-setup] pyenv-virtualenv plugin not detected (missing 'pyenv virtualenv')." >&2
  exit 2
fi

echo "[pyenv-setup] root=$ROOT_DIR"
echo "[pyenv-setup] env=$ENV_NAME"
echo "[pyenv-setup] python_base=$PY_VER"
echo "[pyenv-setup] with_rnc=$WITH_RNC"
echo "[pyenv-setup] check_only=$CHECK_ONLY"

if [[ "$CHECK_ONLY" != "yes" ]]; then
  if ! pyenv versions --bare | grep -Fxq "$ENV_NAME"; then
    echo "[pyenv-setup] creating env '$ENV_NAME'..."
    pyenv install -s "$PY_VER"
    pyenv virtualenv "$PY_VER" "$ENV_NAME"
  else
    echo "[pyenv-setup] env '$ENV_NAME' already exists."
  fi

  echo "[pyenv-setup] installing core requirements..."
  PYENV_VERSION="$ENV_NAME" pyenv exec python -m pip install --upgrade pip setuptools wheel
  PYENV_VERSION="$ENV_NAME" pyenv exec python -m pip install -r "$CORE_REQ"

  if [[ "$WITH_RNC" == "yes" ]]; then
    echo "[pyenv-setup] installing RNC requirements..."
    PYENV_VERSION="$ENV_NAME" pyenv exec python -m pip install -r "$RNC_REQ"
  fi

  if [[ "$SET_LOCAL" == "yes" ]]; then
    echo "[pyenv-setup] setting local pyenv to '$ENV_NAME'..."
    (
      cd "$ROOT_DIR"
      pyenv local "$ENV_NAME"
    )
  fi
fi

echo "[pyenv-setup] diagnostics:"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/matplotlib-codex}"
PYENV_VERSION="$ENV_NAME" pyenv exec python - <<'PY'
import importlib
import sys

mods = [
    "obspy",
    "numpy",
    "pandas",
    "matplotlib",
    "tensorflow",
]

print(f"python_executable={sys.executable}")
print(f"python_version={sys.version.split()[0]}")
missing = []
for name in mods:
    try:
        mod = importlib.import_module(name)
        print(f"{name}=OK:{getattr(mod, '__version__', 'unknown')}")
    except Exception as e:
        missing.append(name)
        print(f"{name}=MISSING:{type(e).__name__}:{e}")

if missing:
    print("missing_modules=" + ",".join(missing))
PY

echo "[pyenv-setup] done."
