# Operacao 0014 - Padrao Verde para API e Source do fluxo legado

**Data:** 2026-02-10  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `legado`

## Objetivo

Alinhar a documentacao do legado ao padrao usado no projeto Verde:

- User Guide -> API docs;
- API docs -> `[source]` -> `_modules`;
- remover scripts Python da secao de artefatos.

## Escopo executado

1. Migracao da navegacao de scripts Python para API/source:
   - `docs/sphinx/source/visao_geral.rst`
   - `docs/sphinx/source/guia/fluxo-e-referencias.rst`
   - `docs/sphinx/source/api/index.rst`

2. Criacao de docs de entrypoints legados na API:
   - `docs/sphinx/source/api/generated/analise_dados.pre_processa.main.rst`
   - `docs/sphinx/source/api/generated/analise_dados.pos_processa.main.rst`
   - `docs/sphinx/source/api/generated/analise_dados.gera_mapas.main.rst`
   - `docs/sphinx/source/api/generated/figures.generate_latex_for_figures.rst`
   - `docs/sphinx/source/api/generated/mapa.generate_map_latex.rst`

3. Ajuste de importacao para gerar `_modules` dos entrypoints:
   - `docs/sphinx/source/conf.py`

4. Remocao de Python da trilha de artefatos:
   - `docs/sphinx/source/artefatos/index.rst`
   - remocao de `docs/sphinx/source/artefatos/*-py.rst`

5. Skill de governanca do padrao:
   - `skills/docs-verde-style/SKILL.md`
   - `skills/docs-verde-style/agents/openai.yaml`
   - `skills/docs-verde-style/references/style-rules.md`

## Resultado

- `Visao Geral` e `User Guide` agora apontam para paginas de docs e source
  interno (`_modules`) em vez de tratar Python como artefato.
- API passou a conter os entrypoints principais do fluxo legado com pagina de
  docs e botao `[source]`.
- Artefatos ficaram restritos a nao-Python (Bash/TXT/TEX).

## Validacao

- Build local:
  - `PYENV_VERSION=sismologia sphinx-build -b html docs/sphinx/source docs/sphinx/build/html`
- Resultado: build concluido com sucesso.

