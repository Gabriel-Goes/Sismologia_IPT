# ROADMAP

## Decisao transversal (2026-03-02)
- Filtro geografico de MG passa a ser deterministico por coordenadas (ponto-poligono).
- Campos `ST`, toponimias e localidades ficam apenas como auditoria de consistencia.

## M0 - Bootstrap cleanroom (done)
- Branch cleanroom criada.
- Snapshot do legado arquivado.
- Estrutura inicial de notebooks e script linear criada.

## M1 - Etapas 1+2: Catalogo e selecao (in progress)
### Goal
Ler catalogo (`QuakeML` ou texto de builder), selecionar eventos alvo e quebrar
em arquivos por evento (`xml|json`) para alimentar a etapa 3.

### Deliverables
- Notebook de selecao (etapas 1+2).
- Export por evento de metadados iniciais.
- Lista de eventos selecionados para aquisicao.

### Verification
- Regras de filtro reproduziveis (regiao, magnitude, profundidade).
- Contagem de eventos antes/depois registrada.

## M1.1 - Alinhamento notebook -> pipeline Python+Bash (planned)
### Goal
Levar para os scripts operacionais a mesma regra validada no notebook Step1:
inclusao de evento em MG por interseccao ponto-poligono, com `ST` apenas para
auditoria.

### Discovery baseline (Step1 RAW)
- `rows_raw_total=5934`
- `rows_keep_in_mg=918`
- `rows_drop_outside_mg=4872`
- `rows_drop_no_valid_coords=144`
- `incons_st_mg_outside=15`
- `incons_st_not_mg_inside=13`
- `incons_st_empty_inside=0`

### Deliverables
- Documentacao de estado atual vs estado alvo em `.specs` e `docs/`.
- Checklist tecnico fechado de migracao para:
  - `scripts/filter_sisbra_csv.py`
  - `scripts/step03_waveforms_from_p_picks.py`
  - `scripts/materialize_events_dataset.py`
  - `scripts/organize_compatible_events.py`
  - `scripts/run_real_mg_maglt4_depthlt10.sh`
- Politica de compatibilidade temporaria:
  - manter `--state`/`--state-filter` na CLI;
  - marcar como parametro de auditoria/deprecacao para gate geografico.

### Verification
- Mesma entrada de catalogo gera contagens iguais entre notebook Step1 e
  pipeline migrado para o gate geografico.
- Tabelas de inconsistencias `ST x geometria` disponiveis para auditoria.
- Sem fallback silencioso para `ST` no criterio de inclusao em MG.

## M2 - Etapa 3: Base local incremental de analise
### Goal
Criar base local por evento com metadados + waveform.

### Deliverables
 **ALGORITMOS DE CELINE HOURCAD SOLICITA ESTRUTURA FIXA. VIDE EXEMPLO ABAIXO:**
#### EXEMPLO DO REPOSITÓRIO DE CELINE HOURCAD
   Dataset
To apply the algorithm, we need a folder architecture:
    - mseed_demo/
        - 2022004T134407/
            - FR_CHLF_2022004T134407.mseed
            - FR_GARF_2022004T134407.mseed
            - FR_GNEF_2022004T134407.mseed
            - FR_VERF_2022004T134407.mseed

#### PROPOSTA DE NOVA ESTRUTURA DE DADOS
**PODEMOS PROPOR ALGO ENTRE O QUE BIANCHI SUGERE E O QUE HOURCAD DEFINE**
    - NDS/
        - YYYYMMDDTHHMMSS/
            - NET_STA_YYYYMMDDTHHMMSS.json **UM PARA CADA EVENTO**
            - NET_STA_YYYYMMDDTHHMMSS.mseed **UM PARA CADA PICK**
        - 2022004T134407/
            - 2022004T134407.json
            - FR_CHLF_2022004T134407.mseed
            - FR_GARF_2022004T134407.mseed
            - FR_GNEF_2022004T134407.mseed
            - FR_VERF_2022004T134407.mseed
**JSON DEVE SER EXPANDÍVEL PARA MAIS INFO COMO RESULTADO DA CNN, SNR, ETC**

### Verification
- Reexecucao nao perde nem duplica eventos ja persistidos.
- Adicao de novos eventos sem reprocessar base completa.

## M3 - Etapa 4: Inferencia CNN paralelizavel
### Goal
Executar inferencia por evento com suporte a paralelismo simples.

### Deliverables
- Script de inferencia por evento.
- Runner de lote paralelo (shell ou python).
- Saida por evento em `prediction.json` ou embutida em `event.json`.  **EMBUTIR EM JSON É ELEGANTE**

### Verification
- Lote de teste executa com resultados consistentes. **LOTE DE TESTES DEVE USAR EVENTOS ALEATÓRIOS DO CATÁLOGO SEMPRE COM 42 COMO SED**
- Escala linear basica ao aumentar workers.

## M4 - Etapa 5: Analise e comunicacao de resultados
### Goal
Consolidar resultados em notebooks para avaliacao cientifica.

### Deliverables
- Notebooks de graficos e mapas.
- Export de tabelas e figuras principais.
- Material pronto para discussao com orientadores.

### Verification
- Pipeline completo reproduzivel em ambiente SEISAPP.
- Resultados

## M5 - Contexto minerario ANM para priorizacao (future)
### Goal
Incorporar vetores oficiais da Agencia Nacional de Mineracao (ANM) para
priorizar eventos em regioes de maior atividade mineraria e apoiar a validacao
dos resultados da rede neural.

### Deliverables
- Ingestao vetorial ANM com versionamento de fonte e data de referencia.
- Camada espacial derivada com atributos relevantes (substancia, estagio da
  atividade, status operacional).
- Regra de priorizacao por proximidade de origem sismica a minas ativas.
- Indicadores de consistencia para classificacao antropogenica:
  - maior confianca quando proximo de atividade mineraria ativa;
  - alerta de possivel falso positivo quando distante de atividade mineraria.

### Verification
- Pipeline espacial reprodutivel e auditavel (mesma entrada -> mesmo resultado).
- Relatorio comparando evento classificado vs contexto minerario de entorno.
- Lista de casos inconsistentes para revisao com professores e responsaveis
  pelo catalogo.
