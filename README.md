# Seismic Event Discriminator (ClassificadorSismologico)

## Ambiente (GeoServer)

Este repo assume uso de `pyenv` e, no GeoServer, o virtualenv `geo-seis` (ObsPy instalado).
O arquivo `.python-version` fixa automaticamente o ambiente ao entrar no diretório.
Nos wrappers (`scripts/run_all_sisbra_build.sh` e `scripts/run_step02.sh`), se `pyenv`
não existir o fallback automático é `python3` (ou `python`).

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
pyenv version
python -c "import obspy; print('obspy ok', obspy.__version__)"
```

## Acesso ao seisArc (FDSNWS) via túnel reverso

Como o `seisArc` só é acessível dentro da rede do IAG, o acesso pelo GeoServer é feito
publicando uma porta local no GeoServer via SSH rodando na SEISAPP (túnel reverso).

Exemplo (rodar na SEISAPP, em paralelo ao keepalive atual):

```bash
nohup ssh -N -T -p 62222 \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -R 127.0.0.1:28080:10.110.0.134:80 \
  ggrl@geodb.duckdns.org \
  >/tmp/tunnel_seisarc_28080.log 2>&1 & disown
```

Teste no GeoServer:

```bash
curl -sS "http://127.0.0.1:28080/fdsnws/event/1/application.wadl" | head
python -c "from obspy.clients.fdsn import Client; c=Client('http://127.0.0.1:28080'); print(c.get_webservice_version())"
```

## Pipeline (SISBRA -> FDSN -> picks export)

1) Associação SISBRA->FDSN via catálogo estático (builder text `catalogs/query.txt`):

```bash
python src/seismic_event_discriminator/step01_catalogo_selecao.py \
  --sisbra-csv catalogs/sisbra/sisbra_v2024May09/catalogo_CLEAN_v2024May09.csv \
  --fdsn-query catalogs/query.txt \
  --n-last 100 \
  --out outputs/sisbra_to_fdsn_last100.csv
```

2) Enriquecimento via FDSN live (seisArc via túnel) e export por evento:

```bash
python src/seismic_event_discriminator/step02_fdsn_picks_export.py \
  --sisbra-csv catalogs/sisbra/sisbra_v2024May09/catalogo_CLEAN_v2024May09.csv \
  --client-url http://127.0.0.1:28080 \
  --workers 1 \
  --n-last 50 \
  --out-root data \
  --max-pick-dist-km 400
```

Saída:

```text
data/YYYYMMDDTHHMMSS_<eventid>_rowNNNN/
  event.xml   (QuakeML do evento FDSN selecionado)
  event.json  (SISBRA + match + picks filtrados < 400 km)
```

## Execução completa (todos os eventos SISBRA)

Para processar todo o catálogo SISBRA e gerar os bundles em lote com log + relatório:

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
bash scripts/run_all_sisbra_build.sh
```

Parâmetros úteis (sem editar script):

```bash
WORKERS=24 N_LAST=0 OUT_ROOT=data/sisbra_all bash scripts/run_all_sisbra_build.sh
```

## Teste paralelo (SEISAPP)

Para um smoke test paralelo antes do lote completo:

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
bash scripts/run_parallel_smoketest_seisapp.sh
```

Defaults do smoke test:
- `WORKERS`: metade dos núcleos (limitado a 24)
- `N_LAST`: 300 eventos mais recentes
- `CLIENT_URL`: `http://seisarc.sismo.iag.usp.br` (SEISAPP)

Arquivos gerados:

- `outputs/logs/run_all_sisbra_<UTC>.log`
- `outputs/logs/run_all_sisbra_<UTC>.md`
- `outputs/logs/run_all_sisbra_<UTC>_summary.csv`

Observação:

- O endpoint UnB (`http://164.41.28.122:5831`) pode estar indisponível por rede/firewall.
  O runner registra essa verificação no relatório.
