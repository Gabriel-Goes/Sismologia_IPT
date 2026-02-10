# Memoria Operacional - Ambiente pyenv + pyenv-virtualenv

Data da verificacao: 2026-02-10
Branch: `refactor/fluxo-v2-documentado`

## Objetivo

Registrar, de forma curta e reutilizavel, como o ambiente Python deste projeto
deve ser configurado e usado para execucao do legado.

## Estado confirmado no host (GeoServer)

- `pyenv` instalado (`pyenv 2.6.20`).
- plugin `pyenv-virtualenv` disponivel.
- Ambientes do projeto existentes:
  - `sismo-core-311` (Python 3.11.9)
  - `sismo-rnc-379` (Python 3.7.9)

## Arquivos canonicos de dependencias

- `scripts/dev/requirements-core-pipeline.txt`
  - stack do pipeline geral (pre, eventos, pos, mapas, relatorio).
- `scripts/dev/requirements-rnc-legacy.txt`
  - stack legado da RNC (inclui TensorFlow 2.8.0).

Observacao: neste repositorio os nomes oficiais sao os acima (com sufixos
`-pipeline` e `-legacy`).

## Bootstrap oficial

Script oficial:

- `scripts/dev/setup_pyenv_dual_envs.sh`

Uso padrao:

```bash
scripts/dev/setup_pyenv_dual_envs.sh
```

Para fixar o ambiente core no repositorio (opcional):

```bash
scripts/dev/setup_pyenv_dual_envs.sh --set-local --skip-rnc
```

## Regra de execucao (ponto critico)

Sem `PYENV_VERSION` (ou sem `.python-version`), o shell pode usar Python do
sistema e gerar erros de dependencia faltante.

Padrao adotado neste repositorio:

- arquivo `.python-version` na raiz com `sismo-core-311`.
- para etapa RNC (`-pr`), sobrescrever explicitamente com
  `PYENV_VERSION=sismo-rnc-379`.

Exemplos observados quando rodamos sem ambiente fixo:

- `ModuleNotFoundError: shapely`
- `ModuleNotFoundError: tqdm`
- `ModuleNotFoundError: seaborn`
- `ModuleNotFoundError: tensorflow`

## Checklist rapido antes de testar

1. Confirmar ambiente ativo:

```bash
PYENV_VERSION=sismo-core-311 python -V
PYENV_VERSION=sismo-rnc-379 python -V
```

2. Rodar pipeline legado (etapas nao-RNC) no core:

```bash
PYENV_VERSION=sismo-core-311 bash .specs/codebase/fluxo_sismo.sh catalogo_jul_filtrado.csv -pe -e -po -m -r -t
```

3. Rodar etapa RNC no ambiente legado:

```bash
PYENV_VERSION=sismo-rnc-379 bash .specs/codebase/fluxo_sismo.sh catalogo_jul_filtrado.csv -pr -t
```

## Decisao registrada

- Mantemos dois ambientes separados por compatibilidade de dependencias.
- O ambiente core nao deve receber TensorFlow legado.
- A etapa `-pr` (RNC) deve ser executada no ambiente `sismo-rnc-379`.
- No `fluxo_sismo.sh`, apenas o comando da predicao usa override de ambiente:

```bash
env PYENV_VERSION="$RNC_PYENV_VERSION" python fonte/rnc/run.py
```

Isso garante que `-pe`, `-e`, `-po`, `-m` e `-r` continuem no ambiente core.
