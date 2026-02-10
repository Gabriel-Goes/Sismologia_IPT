#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Uso:
  scripts/dev/run_fluxo_test_matrix_archived.sh [opcoes]

Executa a matriz padrao de testes do fluxo_sismo.sh em uma copia isolada
(/tmp) e arquiva os artefatos no repositorio para validacao historica.

Opcoes:
  --catalog <arquivo>       Catalogo em arquivos/catalogo (default: catalogo_jul_filtrado.csv)
  --test-limit <n>          Limite de eventos no modo --test (default: 50)
  --core-env <nome>         PYENV_VERSION base do fluxo (default: sismo-core-311)
  --rnc-env <nome>          Ambiente da etapa -pr (default: sismo-rnc-379)
  --cases <lista>           Casos separados por virgula
                            opcoes: pre,eventos,predict,pos,maps,report,todos
                            default: pre,eventos,predict,pos,maps,report,todos
  --archive-root <path>     Diretorio de arquivamento (default: .specs/.../test_matrix)
  --archive-id <id>         Nome do subdiretorio de arquivamento (default: timestamp)
  --run-dir <path>          Diretorio isolado temporario (default: mktemp em /tmp)
  --keep-run-dir            Nao remove o diretorio isolado ao final
  --skip-results            Arquiva apenas logs/summary (nao copia CSV/PDF de resultados)
  --dry-run                 Mostra comandos sem executar
  -h, --help                Mostra esta ajuda

Exemplos:
  scripts/dev/run_fluxo_test_matrix_archived.sh
  scripts/dev/run_fluxo_test_matrix_archived.sh --cases pre,predict,report --test-limit 25
  scripts/dev/run_fluxo_test_matrix_archived.sh --archive-id 20260210_155407
EOF
}

log() {
    echo "[matrix-archive] $*"
}

die() {
    echo "[matrix-archive] ERRO: $*" >&2
    exit 1
}

run_cmd() {
    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] $*"
        return 0
    fi
    "$@"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$REPO_ROOT" ]] || die "nao foi possivel localizar a raiz do repositorio."

CATALOG="catalogo_jul_filtrado.csv"
TEST_LIMIT="50"
CORE_ENV="sismo-core-311"
RNC_ENV="sismo-rnc-379"
CASES_CSV="pre,eventos,predict,pos,maps,report,todos"
ARCHIVE_ROOT="$REPO_ROOT/.specs/codebase/arquivos/registros/test_matrix"
ARCHIVE_ID=""
RUN_DIR=""
KEEP_RUN_DIR=0
SKIP_RESULTS=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --catalog)
            CATALOG="${2:-}"
            [[ -n "$CATALOG" ]] || die "--catalog requer valor."
            shift 2
            ;;
        --test-limit)
            TEST_LIMIT="${2:-}"
            [[ "$TEST_LIMIT" =~ ^[0-9]+$ ]] || die "--test-limit deve ser inteiro >= 0."
            shift 2
            ;;
        --core-env)
            CORE_ENV="${2:-}"
            [[ -n "$CORE_ENV" ]] || die "--core-env requer valor."
            shift 2
            ;;
        --rnc-env)
            RNC_ENV="${2:-}"
            [[ -n "$RNC_ENV" ]] || die "--rnc-env requer valor."
            shift 2
            ;;
        --cases)
            CASES_CSV="${2:-}"
            [[ -n "$CASES_CSV" ]] || die "--cases requer valor."
            shift 2
            ;;
        --archive-root)
            ARCHIVE_ROOT="${2:-}"
            [[ -n "$ARCHIVE_ROOT" ]] || die "--archive-root requer valor."
            shift 2
            ;;
        --archive-id)
            ARCHIVE_ID="${2:-}"
            [[ -n "$ARCHIVE_ID" ]] || die "--archive-id requer valor."
            shift 2
            ;;
        --run-dir)
            RUN_DIR="${2:-}"
            [[ -n "$RUN_DIR" ]] || die "--run-dir requer valor."
            shift 2
            ;;
        --keep-run-dir)
            KEEP_RUN_DIR=1
            shift
            ;;
        --skip-results)
            SKIP_RESULTS=1
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

CODEBASE_SRC="$REPO_ROOT/.specs/codebase"
[[ -d "$CODEBASE_SRC" ]] || die "diretorio nao encontrado: $CODEBASE_SRC"

if [[ -z "$ARCHIVE_ID" ]]; then
    ARCHIVE_ID="$(date +%Y%m%d_%H%M%S)"
fi

if [[ -z "$RUN_DIR" ]]; then
    RUN_DIR="$(mktemp -d -t classificador-matrix-XXXXXX)"
else
    [[ ! -e "$RUN_DIR" ]] || die "run-dir ja existe: $RUN_DIR"
    run_cmd mkdir -p "$RUN_DIR"
fi

cleanup() {
    if [[ "$KEEP_RUN_DIR" -eq 1 ]]; then
        log "run-dir preservado: $RUN_DIR"
        return
    fi
    if [[ "$DRY_RUN" -eq 1 ]]; then
        return
    fi
    rm -rf "$RUN_DIR" >/dev/null 2>&1 || true
}
trap cleanup EXIT

IFS=',' read -r -a CASES <<< "$CASES_CSV"
[[ "${#CASES[@]}" -gt 0 ]] || die "nenhum caso informado em --cases."

for case_name in "${CASES[@]}"; do
    case "$case_name" in
        pre|eventos|predict|pos|maps|report|todos) ;;
        *) die "caso invalido em --cases: $case_name" ;;
    esac
done

log "Repositorio: $REPO_ROOT"
log "Codebase origem: $CODEBASE_SRC"
log "Run dir: $RUN_DIR"
log "Archive root: $ARCHIVE_ROOT"
log "Archive id: $ARCHIVE_ID"
log "Catalogo: $CATALOG"
log "Test limit: $TEST_LIMIT"
log "Core env: $CORE_ENV"
log "RNC env : $RNC_ENV"
log "Casos   : ${CASES[*]}"

run_cmd cp -a "$CODEBASE_SRC/." "$RUN_DIR/"
# Limpa rastros de execucoes antigas vindos do baseline copiado.
if [[ "$DRY_RUN" -eq 0 ]]; then
    rm -rf "$RUN_DIR/arquivos/registros/test_matrix"
else
    echo "[dry-run] rm -rf $RUN_DIR/arquivos/registros/test_matrix"
fi
run_cmd mkdir -p "$RUN_DIR/arquivos/registros/test_matrix"

SUMMARY_FILE="$RUN_DIR/arquivos/registros/test_matrix/summary_${ARCHIVE_ID}.tsv"
if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] printf 'case\\trc\\tduration_s\\ttimeout_s\\tlog\\n' > '$SUMMARY_FILE'"
else
    printf 'case\trc\tduration_s\ttimeout_s\tlog\n' > "$SUMMARY_FILE"
fi

run_case() {
    local name="$1"
    local timeout_s
    local args=()
    local log_file
    local start
    local rc=0
    local duration

    case "$name" in
        pre) timeout_s=240; args=(-pe -t) ;;
        eventos) timeout_s=120; args=(-e -t) ;;
        predict) timeout_s=300; args=(-pr -t) ;;
        pos) timeout_s=240; args=(-po -t) ;;
        maps) timeout_s=180; args=(-m -t) ;;
        report) timeout_s=240; args=(-r -t) ;;
        todos) timeout_s=900; args=(-pe -e -pr -po -m -r -t) ;;
        *) die "caso nao suportado: $name" ;;
    esac

    log_file="$RUN_DIR/arquivos/registros/test_matrix/${name}_${ARCHIVE_ID}.log"
    start="$(date +%s)"

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] env TEST_EVENT_LIMIT=$TEST_LIMIT PYENV_VERSION=$CORE_ENV RNC_PYENV_VERSION=$RNC_ENV timeout -k 10 $timeout_s bash ./fluxo_sismo.sh $CATALOG ${args[*]} > $log_file 2>&1"
        rc=0
    else
        if env \
            TEST_EVENT_LIMIT="$TEST_LIMIT" \
            PYENV_VERSION="$CORE_ENV" \
            RNC_PYENV_VERSION="$RNC_ENV" \
            timeout -k 10 "$timeout_s" \
            bash "$RUN_DIR/fluxo_sismo.sh" "$CATALOG" "${args[@]}" > "$log_file" 2>&1; then
            rc=0
        else
            rc=$?
        fi
    fi

    duration="$(( $(date +%s) - start ))"
    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] append summary line for $name"
    else
        printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$rc" "$duration" "$timeout_s" "arquivos/registros/test_matrix/$(basename "$log_file")" >> "$SUMMARY_FILE"
    fi
    log "case=$name rc=$rc duration=${duration}s log=$(basename "$log_file")"
}

for case_name in "${CASES[@]}"; do
    run_case "$case_name"
done

ARCHIVE_DIR="$ARCHIVE_ROOT/$ARCHIVE_ID"
run_cmd mkdir -p "$ARCHIVE_DIR"

if [[ "$DRY_RUN" -eq 0 ]]; then
    cp -a "$RUN_DIR/arquivos/registros/test_matrix/." "$ARCHIVE_DIR/"
    [[ -f "$RUN_DIR/arquivos/registros/Sismo_Pipeline.log" ]] && cp -a "$RUN_DIR/arquivos/registros/Sismo_Pipeline.log" "$ARCHIVE_DIR/"

    if [[ "$SKIP_RESULTS" -eq 0 ]]; then
        mkdir -p "$ARCHIVE_DIR/resultados"
        for file in \
            "$RUN_DIR/arquivos/resultados/pre_processado.csv" \
            "$RUN_DIR/arquivos/resultados/predito.csv" \
            "$RUN_DIR/arquivos/resultados/erros.csv" \
            "$RUN_DIR/arquivos/resultados/analisado_final.csv"; do
            [[ -f "$file" ]] && cp -a "$file" "$ARCHIVE_DIR/resultados/"
        done

        if [[ -f "$RUN_DIR/arquivos/resultados/relatorios/relatorio_preditivo.pdf" ]]; then
            mkdir -p "$ARCHIVE_DIR/resultados/relatorios"
            cp -a "$RUN_DIR/arquivos/resultados/relatorios/relatorio_preditivo.pdf" "$ARCHIVE_DIR/resultados/relatorios/"
        fi
    fi

    {
        echo "archive_id=$ARCHIVE_ID"
        echo "created_at=$(date -Is)"
        echo "catalog=$CATALOG"
        echo "test_limit=$TEST_LIMIT"
        echo "core_env=$CORE_ENV"
        echo "rnc_env=$RNC_ENV"
        echo "cases=${CASES_CSV}"
        echo "run_dir=$RUN_DIR"
        echo "archive_dir=$ARCHIVE_DIR"
    } > "$ARCHIVE_DIR/manifest.env"
fi

log "arquivamento concluido em: $ARCHIVE_DIR"
log "summary: $ARCHIVE_DIR/summary_${ARCHIVE_ID}.tsv"
