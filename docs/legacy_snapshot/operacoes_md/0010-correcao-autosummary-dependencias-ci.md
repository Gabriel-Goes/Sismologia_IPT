# Operacao 0010 - Correcao do autosummary no CI de documentacao

**Data:** 2026-02-10  
**Branch:** `main`

## Objetivo

Corrigir falha do workflow de docs no GitHub Actions durante o build do Sphinx
com `autosummary`.

## Erro observado

No runner do Actions, o build falhava ao importar:

- `analise_dados.gera_mapas.plot_macroregions`

Falha raiz no log:

- `ModuleNotFoundError: No module named 'pandas'`

Como o import do modulo quebrava, o `autosummary` tambem reportava:

- `AttributeError: module 'analise_dados' has no attribute 'gera_mapas'`

## Causa raiz

O ambiente do runner de CI instala apenas dependencias do Sphinx. Bibliotecas da
baseline (como `pandas` e `numpy`) nao estavam instaladas, e faltava mock
dessas dependencias no `conf.py`.

## Ajuste aplicado

Arquivo alterado:

- `docs/sphinx/source/conf.py`

Mudanca:

- inclusao de `pandas` e `numpy` em `autodoc_mock_imports`.

## Resultado esperado

- `autosummary` consegue importar os modulos-alvo via mocks;
- o build de docs no GitHub Actions deixa de falhar por falta de `pandas`.

## Validacao local

Comando:

```bash
PYENV_VERSION=sismologia sphinx-build -b html docs/sphinx/source docs/sphinx/build/html
```

Resultado:

- build concluido com sucesso.
