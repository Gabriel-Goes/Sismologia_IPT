# Operacao 0015 - Correcao do deploy gh-pages para workspace sujo

**Data:** 2026-02-10  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `refatoracao`

## Objetivo

Corrigir falha de deploy no workflow de docs quando o build do Sphinx altera
arquivos rastreados (ex.: `mapa.tex`) antes do checkout da branch `gh-pages`.

## Escopo executado

1. Ajuste no workflow:
   - `.github/workflows/docs.yml`

2. Medida aplicada antes de trocar para `gh-pages`:
   - `git reset --hard HEAD`
   - `git clean -fd`

## Resultado

- O job de publicacao deixa de falhar com erro:
  - `Your local changes to the following files would be overwritten by checkout`
- O fluxo passa a publicar a partir de um workspace limpo.

## Validacao

- Reproducao do erro original via log de Actions.
- Correcao aplicada no passo `Publish to gh-pages`.

