#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  scripts/dev/run_fluxo_isolated.sh [options] -- <args do fluxo_sismo.sh>

Options:
  --ref <git-ref>         Commit/branch/tag usado no worktree (default: HEAD)
  --worktree-dir <path>   Diretorio do worktree (default: mktemp em /tmp)
  --keep-worktree         Nao remove o worktree ao final
  -h, --help              Mostra esta ajuda

Examples:
  scripts/dev/run_fluxo_isolated.sh -- catalogo_jul.csv -e -t
  scripts/dev/run_fluxo_isolated.sh --ref HEAD~1 -- catalogo_jul.csv -pe
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"

if [[ -z "$REPO_ROOT" ]]; then
    echo "Erro: nao foi possivel localizar a raiz do repositorio via git." >&2
    exit 1
fi

REF="HEAD"
KEEP_WORKTREE=0
WORKTREE_DIR=""
WORKTREE_ADDED=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --ref)
            REF="${2:-}"
            if [[ -z "$REF" ]]; then
                echo "Erro: --ref requer um valor." >&2
                exit 1
            fi
            shift 2
            ;;
        --worktree-dir)
            WORKTREE_DIR="${2:-}"
            if [[ -z "$WORKTREE_DIR" ]]; then
                echo "Erro: --worktree-dir requer um caminho." >&2
                exit 1
            fi
            shift 2
            ;;
        --keep-worktree)
            KEEP_WORKTREE=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            break
            ;;
        *)
            break
            ;;
    esac
done

if [[ $# -eq 0 ]]; then
    echo "Erro: informe os argumentos do fluxo_sismo.sh apos '--'." >&2
    usage
    exit 1
fi

if [[ -z "$WORKTREE_DIR" ]]; then
    WORKTREE_DIR="$(mktemp -d -t classificador-fluxo-XXXXXX)"
else
    if [[ -e "$WORKTREE_DIR" ]]; then
        echo "Erro: diretorio '$WORKTREE_DIR' ja existe. Use outro caminho." >&2
        exit 1
    fi
    mkdir -p "$WORKTREE_DIR"
fi

cleanup() {
    if [[ "$KEEP_WORKTREE" -eq 1 ]]; then
        echo "Worktree preservado em: $WORKTREE_DIR"
        return
    fi

    if [[ "$WORKTREE_ADDED" -eq 1 ]]; then
        git -C "$REPO_ROOT" worktree remove --force "$WORKTREE_DIR" >/dev/null 2>&1 || true
    fi
    rm -rf "$WORKTREE_DIR" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Criando worktree isolado em: $WORKTREE_DIR (ref: $REF)"
git -C "$REPO_ROOT" worktree add --detach "$WORKTREE_DIR" "$REF" >/dev/null
WORKTREE_ADDED=1

FLOW_DIR="$WORKTREE_DIR/.specs/codebase"
if [[ ! -f "$FLOW_DIR/fluxo_sismo.sh" ]]; then
    echo "Erro: '$FLOW_DIR/fluxo_sismo.sh' nao encontrado no worktree." >&2
    exit 1
fi

echo "Executando em ambiente isolado:"
echo "  cd $FLOW_DIR && bash ./fluxo_sismo.sh $*"

set +e
(
    cd "$FLOW_DIR"
    bash ./fluxo_sismo.sh "$@"
)
RC=$?
set -e

if [[ "$RC" -eq 0 ]]; then
    echo "fluxo_sismo.sh concluiu com sucesso."
else
    echo "fluxo_sismo.sh finalizou com erro (exit code: $RC)." >&2
fi

exit "$RC"
