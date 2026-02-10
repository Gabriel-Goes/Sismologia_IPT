#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  scripts/dev/setup_pyenv_dual_envs.sh [options]

Options:
  --core-python <version>   Python do ambiente principal (default: 3.11.9)
  --core-env <name>         Nome do ambiente principal (default: sismo-core-311)
  --rnc-python <version>    Python do ambiente legado RNC (default: 3.7.9)
  --rnc-env <name>          Nome do ambiente legado RNC (default: sismo-rnc-379)
  --create-only             Cria versoes/envs sem instalar pacotes
  --skip-core               Nao processa ambiente principal
  --skip-rnc                Nao processa ambiente legado RNC
  --set-local               Executa pyenv local <core-env> na raiz do repositorio
  --dry-run                 Mostra o que seria executado sem aplicar mudancas
  -h, --help                Mostra esta ajuda

Examples:
  scripts/dev/setup_pyenv_dual_envs.sh --dry-run
  scripts/dev/setup_pyenv_dual_envs.sh --set-local
  scripts/dev/setup_pyenv_dual_envs.sh --core-env geo-seis --skip-rnc
EOF
}

log() {
    echo "[setup-pyenv] $*"
}

die() {
    echo "[setup-pyenv] ERRO: $*" >&2
    exit 1
}

run_cmd() {
    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] $*"
        return 0
    fi
    "$@"
}

ensure_cmd() {
    local cmd="$1"
    command -v "$cmd" >/dev/null 2>&1 || die "comando '$cmd' nao encontrado no PATH."
}

pyenv_has_version() {
    local version="$1"
    local line
    local found=1
    while IFS= read -r line; do
        [[ "$line" == "$version" ]] && found=0
    done < <(pyenv versions --bare)
    return "$found"
}

pyenv_has_virtualenv() {
    local env_name="$1"
    local line
    local found=1
    while IFS= read -r line; do
        [[ "$line" == "$env_name" ]] && found=0
    done < <(pyenv virtualenvs --bare)
    return "$found"
}

install_python_if_missing() {
    local version="$1"
    if pyenv_has_version "$version"; then
        log "Python $version ja instalado."
        return 0
    fi
    log "Instalando Python $version via pyenv..."
    run_cmd pyenv install "$version"
}

create_virtualenv_if_missing() {
    local version="$1"
    local env_name="$2"
    if pyenv_has_virtualenv "$env_name"; then
        log "Virtualenv '$env_name' ja existe."
        return 0
    fi
    log "Criando virtualenv '$env_name' (Python $version)..."
    run_cmd pyenv virtualenv "$version" "$env_name"
}

install_requirements() {
    local env_name="$1"
    local req_file="$2"
    [[ -f "$req_file" ]] || die "arquivo de requirements nao encontrado: $req_file"

    log "Atualizando pip/setuptools/wheel no ambiente '$env_name'..."
    run_cmd env PYENV_VERSION="$env_name" python -m pip install --upgrade pip setuptools wheel

    log "Instalando dependencias de '$req_file' no ambiente '$env_name'..."
    run_cmd env PYENV_VERSION="$env_name" python -m pip install -r "$req_file"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$REPO_ROOT" ]] || die "nao foi possivel localizar a raiz do repositorio."

CORE_PYTHON="3.11.9"
CORE_ENV="sismo-core-311"
RNC_PYTHON="3.7.9"
RNC_ENV="sismo-rnc-379"
CREATE_ONLY=0
SKIP_CORE=0
SKIP_RNC=0
SET_LOCAL=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --core-python)
            CORE_PYTHON="${2:-}"
            [[ -n "$CORE_PYTHON" ]] || die "--core-python requer valor."
            shift 2
            ;;
        --core-env)
            CORE_ENV="${2:-}"
            [[ -n "$CORE_ENV" ]] || die "--core-env requer valor."
            shift 2
            ;;
        --rnc-python)
            RNC_PYTHON="${2:-}"
            [[ -n "$RNC_PYTHON" ]] || die "--rnc-python requer valor."
            shift 2
            ;;
        --rnc-env)
            RNC_ENV="${2:-}"
            [[ -n "$RNC_ENV" ]] || die "--rnc-env requer valor."
            shift 2
            ;;
        --create-only)
            CREATE_ONLY=1
            shift
            ;;
        --skip-core)
            SKIP_CORE=1
            shift
            ;;
        --skip-rnc)
            SKIP_RNC=1
            shift
            ;;
        --set-local)
            SET_LOCAL=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "opcao invalida: $1"
            ;;
    esac
done

if [[ "$SKIP_CORE" -eq 1 && "$SKIP_RNC" -eq 1 ]]; then
    die "nada para fazer: --skip-core e --skip-rnc ativos ao mesmo tempo."
fi

ensure_cmd pyenv

if ! pyenv commands | grep -Fxq "virtualenv"; then
    die "plugin pyenv-virtualenv nao encontrado (comando 'pyenv virtualenv')."
fi

CORE_REQ="$SCRIPT_DIR/requirements-core-pipeline.txt"
RNC_REQ="$SCRIPT_DIR/requirements-rnc-legacy.txt"

log "Repositorio: $REPO_ROOT"
log "Core: env='$CORE_ENV' python='$CORE_PYTHON'"
log "RNC : env='$RNC_ENV' python='$RNC_PYTHON'"

if [[ "$SKIP_CORE" -eq 0 ]]; then
    install_python_if_missing "$CORE_PYTHON"
    create_virtualenv_if_missing "$CORE_PYTHON" "$CORE_ENV"
    if [[ "$CREATE_ONLY" -eq 0 ]]; then
        install_requirements "$CORE_ENV" "$CORE_REQ"
    fi
fi

if [[ "$SKIP_RNC" -eq 0 ]]; then
    install_python_if_missing "$RNC_PYTHON"
    create_virtualenv_if_missing "$RNC_PYTHON" "$RNC_ENV"
    if [[ "$CREATE_ONLY" -eq 0 ]]; then
        install_requirements "$RNC_ENV" "$RNC_REQ"
    fi
fi

if [[ "$SET_LOCAL" -eq 1 ]]; then
    if [[ "$SKIP_CORE" -eq 1 ]]; then
        die "--set-local requer ambiente core ativo (sem --skip-core)."
    fi
    log "Configurando pyenv local '$CORE_ENV' em '$REPO_ROOT'..."
    run_cmd pyenv -C "$REPO_ROOT" local "$CORE_ENV"
fi

log "Concluido."
log "Sugestao de uso:"
log "  PYENV_VERSION=$CORE_ENV scripts/dev/run_fluxo_isolated.sh -- catalogo_jul_filtrado.csv -m"
log "  PYENV_VERSION=$RNC_ENV python .specs/codebase/fonte/rnc/run.py --help"
