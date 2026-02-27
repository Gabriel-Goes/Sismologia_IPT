# Fluxo MG Compativel (Step02 + Step03 + Organizacao)

Este fluxo gera dois conjuntos finais:
- `data/eventos_compativeis`: apenas eventos prontos para classificacao
- `data/eventos_nao_compativeis`: eventos fora dos criterios ou sem onda P utilizavel

## Criterios de Compatibilidade
- `match_status == matched`
- `ST == MG`
- `magnitude < 4`
- `depth_km < 10`
- existe pelo menos 1 pick `P*` com `dist_km <= 400`
- forma de onda baixada em janela `P-10s` a `P+50s`
- precisa haver pelo menos um conjunto 3C por estacao com canais: `HHZ`, `HHN`, `HHE`

## Nomenclatura de Diretorio Final
- Em `eventos_compativeis`, o nome do diretorio e **somente**:
  - `YYYYMMDDTHHMMSS`
- Nao inclui `usp...`, `row...`, etc.
- Se houver colisao de datetime, o evento vai para `eventos_nao_compativeis` com motivo `datetime_collision`.

## Arquivos e Scripts
- Step02 (bundles): `src/seismic_event_discriminator/step02_fdsn_picks_export.py`
- Step03 (ondas por pick P): `scripts/step03_waveforms_from_p_picks.py`
- Organizacao final: `scripts/organize_compatible_events.py`

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
        try: mag=float(row.get('mag',''))
        except: continue
        try: dep=float(row.get('depth',''))
        except: continue
        if st=='MG' and mag<4 and dep<10:
            rows.append(row)
with open(out,'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fn); w.writeheader(); w.writerows(rows)
print(out, len(rows))
PY
```

2. Executar Step02 no subconjunto:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && LOG_DIR=outputs/logs_mg_maglt4_depthlt10_w24 WORKERS=24 N_LAST=0 OUT_ROOT=data/sisbra_mg_maglt4_depthlt10_w24 SISBRA_CSV=outputs/sisbra_mg_maglt4_depthlt10.csv CLIENT_URL=http://127.0.0.1:28080 bash scripts/run_all_sisbra_build.sh
```

3. Baixar formas de onda (60 s = P-10 / P+50):
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/step03_waveforms_from_p_picks.py --events-root data/sisbra_mg_maglt4_depthlt10_w24 --client-url http://127.0.0.1:28080 --max-pick-dist-km 400 --pre-p-s 10 --post-p-s 50 --workers 12 --state-filter MG --max-mag 4 --max-depth-km 10 --component-channels HHZ,HHN,HHE --summary-csv outputs/waveform_triplet_download_summary_mg.csv
```

4. Organizar compativeis/incompativeis:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/organize_compatible_events.py --events-root data/sisbra_mg_maglt4_depthlt10_w24 --download-summary-csv outputs/waveform_triplet_download_summary_mg.csv --compatible-root data/eventos_compativeis --incompatible-root data/eventos_nao_compativeis --state-filter MG --max-mag 4 --max-depth-km 10 --max-pick-dist-km 400 --report-csv outputs/eventos_compatibilidade_report.csv --report-md outputs/eventos_compatibilidade_report.md
```

5. Enforce de triplet HHZ/HHN/HHE em `eventos_compativeis`:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/enforce_triplet_channels.py --compatible-root data/eventos_compativeis --incompatible-root data/eventos_nao_compativeis --required-channels HHZ,HHN,HHE --report-csv outputs/eventos_triplet_filter_report.csv --report-md outputs/eventos_triplet_filter_report.md
```

## Auditoria
- Relatorio por evento: `outputs/eventos_compatibilidade_report.csv`
- Relatorio resumido: `outputs/eventos_compatibilidade_report.md`
- Resumo de download por pick/canal: `outputs/waveform_triplet_download_summary_mg.csv`
- Relatorio de filtro por triplet: `outputs/eventos_triplet_filter_report.md`
