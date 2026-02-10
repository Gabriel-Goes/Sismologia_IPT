# Operacao 0012 - Ordenacao de metodos no topo da API (branch de preview)

**Data:** 2026-02-10  
**Branch:** `docs/api-topo-preview`

## Objetivo

Manter as paginas de API com assinatura/metodo no topo, no estilo visual do
`autosummary` original, sem voltar a sobrescrever os textos explicativos.

## O que foi ajustado

Arquivos alterados:

- `docs/sphinx/source/api/generated/*.rst` (14 paginas)

Mudanca aplicada:

- bloco `.. currentmodule::` + `.. autofunction::`/`.. autoclass::` movido para
  o topo da pagina, logo abaixo do titulo.

Efeito:

- o leitor ve primeiro a definicao tecnica do objeto;
- em seguida le o texto explicativo (`Resumo`, `Parametros`, `Retorno`, etc.).

## Decisao de estrategia

- **ajustado**: `autosummary_generate = True`
- **ajustado**: `autosummary_generate_overwrite = False` (modo hibrido)
- **mantido**: descricao manual detalhada por metodo
- **ajustado**: ordem de apresentacao para priorizar assinatura no topo

Com esse modo hibrido, novas paginas podem ser geradas automaticamente quando
necessario, sem sobrescrever as paginas ja editadas manualmente.

## Validacao local

Comando:

```bash
PYENV_VERSION=sismologia sphinx-build -b html docs/sphinx/source docs/sphinx/build/html
```

Resultado:

- build concluido com sucesso;
- paginas renderizadas com assinatura no topo e descricao abaixo.

## Incremento (mesmo contexto)

Foi criada a skill `operation-journal-consolidator` para padronizar a decisao
entre:

- consolidar mudancas na ultima operacao;
- abrir uma nova operacao numerada.

Arquivos da skill:

- `skills/operation-journal-consolidator/SKILL.md`
- `skills/operation-journal-consolidator/references/relatedness-rules.md`

## Publicacao sem commit em `main`

Esta operacao foi feita em branch separada para evitar gatilho de notificacoes
em `main`. A publicacao pode ser testada no `gh-pages` via `workflow_dispatch`
apontando para esta branch, e o merge para `main` fica para depois da validacao.
