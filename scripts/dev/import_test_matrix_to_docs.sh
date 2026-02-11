#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Uso:
  scripts/dev/import_test_matrix_to_docs.sh [opcoes]

Importa artefatos de uma execucao em
.specs/codebase/arquivos/registros/test_matrix/<archive_id>
para docs/operacoes/anexos e cria/atualiza paginas em docs/sphinx/source/anexos.

Opcoes:
  --archive-id <id>      ID da execucao (default: ultimo diretorio em test_matrix)
  --op-tag <tag>         Prefixo dos anexos (ex.: 0025b, 0026a) [obrigatorio]
  --files <lista>        Itens separados por virgula
                         default: summary,manifest,predict,pos,report,pre_processado,predito,analisado_final,erros
  --dry-run              Mostra acoes sem alterar arquivos
  -h, --help             Mostra ajuda

Itens suportados em --files:
  summary,manifest,pre,eventos,predict,pos,maps,report,todos,
  pre_processado,predito,analisado_final,erros
EOF
}

die() {
    echo "[import-test-matrix] ERRO: $*" >&2
    exit 1
}

log() {
    echo "[import-test-matrix] $*"
}

run_cmd() {
    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] $*"
        return 0
    fi
    "$@"
}

to_hyphen() {
    echo "$1" | tr '_' '-'
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$REPO_ROOT" ]] || die "nao foi possivel localizar a raiz do repositorio."

ARCHIVE_ROOT="$REPO_ROOT/.specs/codebase/arquivos/registros/test_matrix"
DOCS_ANEXOS="$REPO_ROOT/docs/operacoes/anexos"
SPHINX_ANEXOS="$REPO_ROOT/docs/sphinx/source/anexos"
SPHINX_INDEX="$SPHINX_ANEXOS/index.rst"

ARCHIVE_ID=""
OP_TAG=""
FILES_CSV="summary,manifest,predict,pos,report,pre_processado,predito,analisado_final,erros"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --archive-id)
            ARCHIVE_ID="${2:-}"
            [[ -n "$ARCHIVE_ID" ]] || die "--archive-id requer valor."
            shift 2
            ;;
        --op-tag)
            OP_TAG="${2:-}"
            [[ -n "$OP_TAG" ]] || die "--op-tag requer valor."
            shift 2
            ;;
        --files)
            FILES_CSV="${2:-}"
            [[ -n "$FILES_CSV" ]] || die "--files requer valor."
            shift 2
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

[[ -n "$OP_TAG" ]] || die "--op-tag e obrigatorio."
[[ -d "$ARCHIVE_ROOT" ]] || die "diretorio nao encontrado: $ARCHIVE_ROOT"
[[ -f "$SPHINX_INDEX" ]] || die "indice Sphinx nao encontrado: $SPHINX_INDEX"

if [[ -z "$ARCHIVE_ID" ]]; then
    ARCHIVE_ID="$(
        find "$ARCHIVE_ROOT" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' \
        | sort | tail -n 1
    )"
    [[ -n "$ARCHIVE_ID" ]] || die "nenhuma execucao encontrada em $ARCHIVE_ROOT"
fi

ARCHIVE_DIR="$ARCHIVE_ROOT/$ARCHIVE_ID"
[[ -d "$ARCHIVE_DIR" ]] || die "execucao nao encontrada: $ARCHIVE_DIR"

run_cmd mkdir -p "$DOCS_ANEXOS" "$SPHINX_ANEXOS"

IFS=',' read -r -a ITEMS <<< "$FILES_CSV"
[[ "${#ITEMS[@]}" -gt 0 ]] || die "nenhum item informado em --files."

created=0
skipped=0

for item in "${ITEMS[@]}"; do
    src=""
    ext=""
    case "$item" in
        summary)
            src="$ARCHIVE_DIR/summary_${ARCHIVE_ID}.tsv"; ext="tsv"
            ;;
        manifest)
            src="$ARCHIVE_DIR/manifest.env"; ext="env"
            ;;
        pre|eventos|predict|pos|maps|report|todos)
            src="$ARCHIVE_DIR/${item}_${ARCHIVE_ID}.log"; ext="log"
            ;;
        pre_processado)
            src="$ARCHIVE_DIR/resultados/pre_processado.csv"; ext="csv"
            ;;
        predito)
            src="$ARCHIVE_DIR/resultados/predito.csv"; ext="csv"
            ;;
        analisado_final)
            src="$ARCHIVE_DIR/resultados/analisado_final.csv"; ext="csv"
            ;;
        erros)
            src="$ARCHIVE_DIR/resultados/erros.csv"; ext="csv"
            ;;
        *)
            die "item nao suportado em --files: $item"
            ;;
    esac

    if [[ ! -f "$src" ]]; then
        log "arquivo ausente para item '$item' (skip): $src"
        skipped=$((skipped + 1))
        continue
    fi

    dst_base="${OP_TAG}-${item}.${ext}"
    dst_file="$DOCS_ANEXOS/$dst_base"
    rst_stub="anexo-${OP_TAG}-$(to_hyphen "$item")-${ext}"
    rst_file="$SPHINX_ANEXOS/${rst_stub}.rst"

    run_cmd cp -f "$src" "$dst_file"

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] gerar $rst_file"
    else
        cat > "$rst_file" <<EOF
Anexo: ${dst_base}
$(printf '%*s' $((7 + ${#dst_base})) '' | tr ' ' '=')

Arquivo de origem:

- :ghblob:\`docs/operacoes/anexos/${dst_base}\`

Conteudo
--------

.. literalinclude:: ../../../../docs/operacoes/anexos/${dst_base}
   :language: text
   :linenos:
EOF
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] garantir entrada no index: $rst_stub"
    else
        if ! grep -Fqx "   ${rst_stub}" "$SPHINX_INDEX"; then
            echo "   ${rst_stub}" >> "$SPHINX_INDEX"
        fi
    fi

    created=$((created + 1))
    log "importado: $item -> $dst_base"
done

log "archive_id: $ARCHIVE_ID"
log "op_tag    : $OP_TAG"
log "itens ok  : $created"
log "itens skip: $skipped"
