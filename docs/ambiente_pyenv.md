# Ambiente Python com pyenv

Este projeto usa `pyenv` no GeoServer para fixar interpretador e dependencias.

## Estado padrao no repositorio

- arquivo local: `.python-version`
- valor atual esperado: `geo-seis`
- comando padrao dos wrappers: `pyenv exec python`

## Bootstrap rapido (GeoServer)

1. Criar/atualizar o ambiente core e fixar no repo:

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
scripts/dev/setup_pyenv_project.sh --env geo-seis --python 3.12.11 --set-local
```

2. Verificar apenas diagnostico (sem instalar nada):

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
scripts/dev/setup_pyenv_project.sh --check-only
```

## Ambiente para inferencia RNC (tensorflow)

Quando precisar executar `run_rnc_eventos_compativeis.py`, recomenda-se ambiente separado.

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
scripts/dev/setup_pyenv_project.sh --env geo-seis-rnc --python 3.11.9 --with-rnc
```

Execucao da RNC com override de ambiente:

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
PYENV_VERSION=geo-seis-rnc pyenv exec python scripts/run_rnc_eventos_compativeis.py --help
```

## Arquivos de dependencia

- core pipeline: `scripts/dev/requirements-core-pipeline.txt`
- rnc inference: `scripts/dev/requirements-rnc-inference.txt`

## Hosts sem pyenv (ex.: SEISAPP)

Sem `pyenv`, executar com `python3` do host e garantir as mesmas libs instaladas no ambiente local.

Exemplo de checagem minima:

```bash
python3 - <<'PY'
mods = ["obspy", "numpy", "pandas"]
for m in mods:
    __import__(m)
print("ok")
PY
```

