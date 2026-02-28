# Seismic Event Discriminator (ClassificadorSismologico)

## Ambiente (GeoServer)

Este repo usa `pyenv` com `.python-version` para fixar o ambiente local no GeoServer.
Ambiente padrão do projeto: `geo-seis`.

Bootstrap/check recomendado:

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
scripts/dev/setup_pyenv_project.sh --env geo-seis --python 3.12.11 --set-local
scripts/dev/setup_pyenv_project.sh --check-only
```

Para RNC (TensorFlow), use ambiente dedicado:

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
scripts/dev/setup_pyenv_project.sh --env geo-seis-rnc --python 3.11.9 --with-rnc
PYENV_VERSION=geo-seis-rnc pyenv exec python scripts/run_rnc_eventos_compativeis.py --help
```

Guia completo: `docs/ambiente_pyenv.md`.

Nos wrappers (`scripts/run_all_sisbra_build.sh` e `scripts/run_step02.sh`), se `pyenv`
não existir, o fallback automático é `python3` (ou `python`).

## Arquitetura e Planejamento

Fonte canônica de arquitetura e planejamento do projeto:
- `.specs/project/`
- `.specs/codebase/`
- `.specs/features/`

Documentacao em `docs/` pode conter material historico e operacional, mas as
decisoes de arquitetura e roadmap devem ser registradas em `.specs/`.

## Scripts Legados de Diagnostico

Os utilitarios de diagnostico historico foram movidos para:
- `scripts/legacy/`

Indice e contexto de uso:
- `scripts/legacy/README.md`

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

Script legado equivalente para keepalive interativo:
- `scripts/legacy/keep_tunnel_seisapp_interativo.sh`

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

O `event.json` exportado pelo Step02 inclui `waveform_download_contract`,
usado pelo Step03 para definir o formato/canais de download por padrao,
incluindo o padrao de nome `NET_STA_DATETIME.mseed`.

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

## Inferencia RNC em `eventos_compativeis`

Modelo legado versionado no repo:
- `models/rnc/model_2021354T1554.h5`

Runner principal (persistencia em `event.json` + CSVs de auditoria):

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
pyenv exec python scripts/run_rnc_eventos_compativeis.py \
  --compatible-root data/eventos_compativeis \
  --model-path models/rnc/model_2021354T1554.h5 \
  --workers 4 \
  --skip-existing \
  --summary-events-csv outputs/rnc_prediction_events.csv \
  --summary-picks-csv outputs/rnc_prediction_picks.csv \
  --summary-errors-csv outputs/rnc_prediction_errors.csv
```

Contrato de saida:
- Atualiza `data/eventos_compativeis/<DATETIME>/event.json` com bloco `rnc_prediction`.
- Gera:
  - `outputs/rnc_prediction_events.csv`
  - `outputs/rnc_prediction_picks.csv`
  - `outputs/rnc_prediction_errors.csv`

Opcional (formato mais proximo do esperado pela RNC original):
- no Step03, ao usar `--component-channels HHZ,HHN,HHE`, o default ja e gerar
  um unico `.mseed` 3C por estacao no formato `NET_STA_DATETIME.mseed`.
- `DATETIME` usa origem do evento em UTC no formato juliano `%Y%jT%H%M%S`
  (ex.: `2022004T134407`).
- para bases antigas no formato split por canal, consolidar `HHZ/HHN/HHE`
  em um unico `.mseed` 3C por estacao com o mesmo padrao:

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
pyenv exec python scripts/merge_triplet_waveforms.py \
  --compatible-root data/eventos_compativeis \
  --waveforms-subdir waveforms \
  --merged-subdir waveforms_3c \
  --required-channels HHZ,HHN,HHE \
  --summary-csv outputs/waveforms_3c_merge_summary.csv
```

Dependencias para etapa RNC:
- `numpy`
- `pandas`
- `obspy`
- `tensorflow`
