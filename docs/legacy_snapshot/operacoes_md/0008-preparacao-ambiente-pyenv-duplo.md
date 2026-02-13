# Operacao 0008 - Preparacao de ambiente com pyenv duplo

**Data:** 2026-02-10
**Branch:** `refactor/fluxo-Alpha-documentado`

## Objetivo

Criar um passo reprodutivel de ambiente de desenvolvimento com `pyenv` +
`pyenv-virtualenv`, separando:

1. ambiente principal do pipeline (`core`);
2. ambiente legado da RNC/TensorFlow (`rnc`).

## Contexto operacional

- Execucao desta fase: **GeoServer** (`ggrl@GeoServer`).
- Reescrita do codigo: planejada para **SEISAPP** (`gabrielgoes@SEISAPP`).
- Restricao atual: ainda sem acesso remoto ao SEISAPP fora da rede fisica do IAG.

Por isso, nesta operacao o foco foi preparar roteiro e automacao de ambiente, e
nao iniciar reescrita funcional dos modulos.

## Motivacao tecnica (a partir da operacao 0007)

Nos testes do `fluxo_sismo.sh`, as falhas recorrentes foram de dependencias
faltantes, por exemplo:

- `shapely` (pre-processamento);
- `tqdm` (fluxo de eventos);
- `tensorflow` (RNC);
- `seaborn` (pos-processamento).

A separacao em dois ambientes reduz conflito de stack (especialmente TensorFlow
legado vs bibliotecas atuais do pipeline).

## Decisao de versoes

1. **Core pipeline**
   - Python: `3.11.9`
   - Virtualenv: `sismo-core-311`
   - Escopo: pre-processamento, aquisicao, pos-processamento, mapas e relatorio.

2. **RNC legado**
   - Python: `3.7.9`
   - Virtualenv: `sismo-rnc-379`
   - Escopo: `fonte/rnc/*` com stack compativel ao historico do modelo
     (`tensorflow==2.8.0`).

## Artefatos criados

1. `scripts/dev/setup_pyenv_dual_envs.sh`
   Script de bootstrap para criar/configurar os dois ambientes.

2. `scripts/dev/requirements-core-pipeline.txt`
   Dependencias do fluxo geral (sem TensorFlow legado).

3. `scripts/dev/requirements-rnc-legacy.txt`
   Dependencias fixadas da stack legado da RNC.

## Evidencias coletadas no GeoServer

1. `pyenv` disponivel no host.
2. `pyenv-virtualenv` disponivel no host.
3. Python ativo no shell atual: `3.13.7`.
4. `pyenv versions` contem `3.11.9` e `3.12.11` instalados.
5. Validacao do script:
   - `bash -n scripts/dev/setup_pyenv_dual_envs.sh` -> `OK`.
   - `scripts/dev/setup_pyenv_dual_envs.sh --help` executado.
   - `scripts/dev/setup_pyenv_dual_envs.sh --dry-run --create-only` executado.

## Procedimento recomendado

### 1) Criar ambientes

```bash
scripts/dev/setup_pyenv_dual_envs.sh
```

### 2) Definir ambiente principal local do repositorio (opcional)

```bash
scripts/dev/setup_pyenv_dual_envs.sh --set-local --skip-rnc
```

### 3) Rodar pipeline legado no ambiente core

```bash
PYENV_VERSION=sismo-core-311 scripts/dev/run_fluxo_isolated.sh -- catalogo_jul_filtrado.csv -m
```

### 4) Rodar RNC no ambiente legado

```bash
PYENV_VERSION=sismo-rnc-379 python .specs/codebase/fonte/rnc/run.py --help
```

## Risco conhecido

`python 3.7.9` e `tensorflow 2.8.0` sao legado e podem exigir ajustes de
dependencias de sistema no servidor alvo (SEISAPP). O roteiro da operacao cobre
o bootstrap Python/pip; pacotes de sistema devem ser validados no host do IAG.

## Conclusao

A base de ambiente para iniciar a refatoracao foi formalizada e automatizada.
O proximo passo e reproduzir esse mesmo bootstrap no SEISAPP quando houver
acesso de rede local no IAG, antes de iniciar a primeira mudanca de codigo.
