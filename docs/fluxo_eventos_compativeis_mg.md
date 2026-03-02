# Fluxo MG Compativel (Step02 + Step03 + Organizacao)

Este fluxo gera dois conjuntos finais:
- `data/eventos_compativeis`: apenas eventos prontos para classificacao
- `data/eventos_nao_compativeis`: eventos fora dos criterios ou sem onda P utilizavel

## Descobertas do Notebook Step1 (RAW + ponto-poligono)
Fonte: `notebooks/step1_sisbra_selfcontained.ipynb` (execucao registrada no notebook).

- `rows_raw_total=5934`
- `rows_keep_in_mg=918`
- `rows_drop_outside_mg=4872`
- `rows_drop_no_valid_coords=144`
- `incons_st_mg_outside=15`
- `incons_st_not_mg_inside=13`
- `incons_st_empty_inside=0`

Conclusao:
- a pergunta "evento ocorreu em MG?" deve ser respondida por coordenadas
  (ponto-poligono), nao por `ST`/toponimia/localidade.
- `ST` deve ficar como trilha de auditoria para detectar inconsistencias do catalogo.

## Estado atual vs estado alvo
- Estado atual (scripts Python+Bash): ainda usa gates por `ST` em partes do fluxo.
- Estado alvo (aprovado): usar gate geografico deterministico em todo o pipeline.
- Impacto atual: notebook e pipeline podem divergir na selecao de eventos em MG.

## Execucao Real (target `data/events`)

Para a execucao operacional que para antes da rede neural, use:

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
bash scripts/run_real_mg_maglt4_depthlt10.sh
```

No codigo atual, este wrapper aplica os criterios estritos:
- `match_status == matched`
- `state == MG`
- `year >= 2020`
- `magnitude < 4`
- `depth_km < 10`
- pick `P*` com `dist_km <= 400`
- janela `P-10s` a `P+50s`
- canais `HHZ,HHN,HHE`

Layout final:
- `data/events/YYYYJJJTHHMMSS/event.json`
- `data/events/YYYYJJJTHHMMSS/event.xml`
- `data/events/YYYYJJJTHHMMSS/waveform/NET_STA_DATETIME.mseed`

Layout de investigacao (nao-matched):
- `data/events_stage_non_matched/ambiguous/*/event.json`
- `data/events_stage_non_matched/no_match/*/event.json`
- `outputs/non_matched_audit.csv`
- `outputs/non_matched_audit.md`
- `outputs/ambiguous_events.csv`
- `outputs/no_match_events.csv`

Observacao:
- eventos `no_match`/`ambiguous` com agencia SISBRA contendo `IAG/USP` sao marcados como
  severidade `critical` na auditoria para investigacao prioritaria.

Regra de seguranca:
- o wrapper aborta se `data/events` nao estiver vazio (nao faz limpeza automatica).
- precheck funcional de endpoint e feito com cliente `obspy` (nao usa `curl`).

## Criterios de Compatibilidade
- Implementado hoje (scripts):
  - `match_status == matched`
  - `ST == MG`
  - `magnitude < 4`
  - `depth_km < 10`
  - existe pelo menos 1 pick `P*` com `dist_km <= 400`
  - forma de onda baixada em janela `P-10s` a `P+50s`
  - precisa haver pelo menos um conjunto 3C por estacao com canais: `HHZ`, `HHN`, `HHE`
- Criterio alvo aprovado (ainda nao migrado no pipeline completo):
  - `inside_mg_polygon == True` (interseccao ponto-poligono)
  - `ST`/toponimia/localidade usados somente para auditoria de consistencia
  - manter os demais gates tecnicos (mag/depth/picks/janela/canais)

## Nomenclatura de Diretorio Final
- Em `eventos_compativeis`, o nome do diretorio e **somente**:
  - `YYYYMMDDTHHMMSS`
- Nao inclui `usp...`, `row...`, etc.
- Se houver colisao de datetime, o evento vai para `eventos_nao_compativeis` com motivo `datetime_collision`.

## Arquivos e Scripts
- Step02 (bundles): `src/seismic_event_discriminator/step02_fdsn_picks_export.py`
- Step03 (ondas por pick P): `scripts/step03_waveforms_from_p_picks.py`
- Organizacao final: `scripts/organize_compatible_events.py`

Observacao:
- O Step02 grava no `event.json` o bloco `waveform_download_contract`
  (modo + canais + padrao de nome). O Step03 usa esse contrato automaticamente quando
  `--component-channels` nao e informado via CLI.
- Setup/check de ambiente pyenv: `docs/ambiente_pyenv.md`.
- Arquitetura e planejamento canonicos: `.specs/project/`, `.specs/codebase/` e `.specs/features/`.
- Scripts de diagnostico historico: `scripts/legacy/`.

## Execucao Recomendada
1. Gerar CSV filtrado MG/M<4/depth<10:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && python3 - <<'PY'
import csv
src='catalogs/sisbra/sisbra_v2024May09/catalogo_CLEAN_v2024May09.csv'
out='outputs/sisbra_mg_maglt4_depthlt10.csv'
rows=[]
with open(src,encoding='utf-8',newline='') as f:
    r=csv.DictReader(f); fn=r.fieldnames
    for row in r:
        st=(row.get('ST') or '').strip().upper()
        try: year=int(row.get('year',''))
        except: continue
        try: mag=float(row.get('mag',''))
        except: continue
        try: dep=float(row.get('depth',''))
        except: continue
        if st=='MG' and year>=2020 and mag<4 and dep<10:
            rows.append(row)
with open(out,'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fn); w.writeheader(); w.writerows(rows)
print(out, len(rows))
PY
```
Observacao: este passo ainda usa `ST` no codigo atual e sera substituido por
filtro ponto-poligono na migracao do pipeline.

2. Executar Step02 no subconjunto:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && LOG_DIR=outputs/logs_mg_maglt4_depthlt10_w24 WORKERS=24 N_LAST=0 OUT_ROOT=data/sisbra_mg_maglt4_depthlt10_w24 SISBRA_CSV=outputs/sisbra_mg_maglt4_depthlt10.csv CLIENT_URL=http://127.0.0.1:28080 bash scripts/run_all_sisbra_build.sh
```

3. Baixar formas de onda (60 s = P-10 / P+50):
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/step03_waveforms_from_p_picks.py --events-root data/sisbra_mg_maglt4_depthlt10_w24 --client-url http://127.0.0.1:28080 --max-pick-dist-km 400 --pre-p-s 10 --post-p-s 50 --workers 12 --state-filter MG --max-mag 4 --max-depth-km 10 --component-channels HHZ,HHN,HHE --summary-csv outputs/waveform_triplet_download_summary_mg.csv
```
- Com `--component-channels HHZ,HHN,HHE`, o default agora e salvar **1 arquivo 3C**
  por estacao no formato `NET_STA_DATETIME.mseed`.
- `DATETIME` usa origem do evento em UTC no formato juliano `%Y%jT%H%M%S`
  (ex.: `2022004T134407`).
- Para manter o modo legado (1 arquivo por canal), adicionar `--split-component-files`.

4. Organizar compativeis/incompativeis:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/organize_compatible_events.py --events-root data/sisbra_mg_maglt4_depthlt10_w24 --download-summary-csv outputs/waveform_triplet_download_summary_mg.csv --compatible-root data/eventos_compativeis --incompatible-root data/eventos_nao_compativeis --state-filter MG --max-mag 4 --max-depth-km 10 --max-pick-dist-km 400 --report-csv outputs/eventos_compatibilidade_report.csv --report-md outputs/eventos_compatibilidade_report.md
```

5. Enforce de triplet HHZ/HHN/HHE em `eventos_compativeis`:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/enforce_triplet_channels.py --compatible-root data/eventos_compativeis --incompatible-root data/eventos_nao_compativeis --required-channels HHZ,HHN,HHE --report-csv outputs/eventos_triplet_filter_report.csv --report-md outputs/eventos_triplet_filter_report.md
```

6. Opcional: consolidar 3 arquivos (`HHZ/HHN/HHE`) em um unico `.mseed` 3C por estacao com nome `NET_STA_DATETIME.mseed`:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/merge_triplet_waveforms.py --compatible-root data/eventos_compativeis --waveforms-subdir waveforms --merged-subdir waveforms_3c --required-channels HHZ,HHN,HHE --summary-csv outputs/waveforms_3c_merge_summary.csv
```

7. Rodar inferencia RNC e persistir resultado no `event.json`:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/run_rnc_eventos_compativeis.py --compatible-root data/eventos_compativeis --model-path models/rnc/model_2021354T1554.h5 --workers 4 --skip-existing --summary-events-csv outputs/rnc_prediction_events.csv --summary-picks-csv outputs/rnc_prediction_picks.csv --summary-errors-csv outputs/rnc_prediction_errors.csv
```

## Auditoria
- Relatorio por evento: `outputs/eventos_compatibilidade_report.csv`
- Relatorio resumido: `outputs/eventos_compatibilidade_report.md`
- Auditoria de nao-matched (consolidado): `outputs/non_matched_audit.csv`
- Auditoria de nao-matched (resumo): `outputs/non_matched_audit.md`
- Lista dedicada de `ambiguous`: `outputs/ambiguous_events.csv`
- Lista dedicada de `no_match`: `outputs/no_match_events.csv`
- Resumo de download por pick/canal: `outputs/waveform_triplet_download_summary_mg.csv`
- Relatorio de filtro por triplet: `outputs/eventos_triplet_filter_report.md`
- Resumo de consolidacao 3C (opcional): `outputs/waveforms_3c_merge_summary.csv`
- Predicao RNC por evento: `outputs/rnc_prediction_events.csv`
- Predicao RNC por pick: `outputs/rnc_prediction_picks.csv`
- Erros da etapa RNC: `outputs/rnc_prediction_errors.csv`
