# Operacao 0005 - Analise historica dos logs do pipeline

**Data:** 2026-02-10
**Branch:** `refactor/fluxo-v2-documentado`

## Objetivo

Documentar o comportamento real do pipeline legado a partir dos logs de
execucao em `.specs/codebase/arquivos/registros/.bkp/`, antes da reescrita do
fluxo.

## Escopo desta leitura

- inventario temporal completo dos logs `Sismo_Pipeline.log.*` pelo timestamp;
- leitura integral dos logs pequenos e medios;
- leitura orientada por amostragem + metricas nos logs gigantes;
- correlacao de cada log com o commit imediatamente anterior no historico Git.

Anexo gerado nesta operacao:

- [0005-resumo-logs.csv](/anexos/anexo-0005-resumo-logs-csv) (210 linhas, um registro por log).

## Metodo aplicado

1. Ordenacao temporal por timestamp do nome do arquivo.
2. Classificacao por tamanho:
   - pequenos: `<= 120 KB`;
   - medios: `> 120 KB` e `<= 2.2 MB`;
   - gigantes: `> 2.2 MB`.
3. Extração de metricas por log:
   - combinacao de etapas executadas (`P/E/R/O/M/T`);
   - status final (`ok`, `trace`, `partial`);
   - contagens de mensagens recorrentes;
   - excecao final (quando existente);
   - commit anterior por data.

## Cobertura

- logs analisados: **210**
- pequenos (leitura integral): **179**
- medios (leitura integral): **21**
- gigantes (leitura integral para metricas + inspeção por amostragem): **10**

## Resultado macro

- status final:
  - `trace`: **98**
  - `partial`: **91**
  - `ok`: **21**
- combinacoes de etapas mais comuns:
  - `P`: **78**
  - `-` (sem etapa de processamento): **43**
  - `E`: **37**
  - `O`: **11**
  - `PE`: **10**

## Evidencias representativas

- sucesso completo com aquisicao de eventos e fechamento do pipeline:
  - `.specs/codebase/arquivos/registros/.bkp/Sismo_Pipeline.log.20240805141037:1895823`
  - `.specs/codebase/arquivos/registros/.bkp/Sismo_Pipeline.log.20240805141037:1895827`
- erro de retorno no fim do fluxo de eventos:
  - `.specs/codebase/arquivos/registros/.bkp/Sismo_Pipeline.log.20240806150022:1087936`
- erro de metadado com variavel nao inicializada:
  - `.specs/codebase/arquivos/registros/.bkp/Sismo_Pipeline.log.20240808141859:492`
- erro de pos-processamento por coluna ausente:
  - `.specs/codebase/arquivos/registros/.bkp/Sismo_Pipeline.log.20241008170339:520569`
- erro de inferencia no `rnc`:
  - `.specs/codebase/arquivos/registros/.bkp/Sismo_Pipeline.log.20241010183245:70`
- erro headless no backend do matplotlib:
  - `.specs/codebase/arquivos/registros/.bkp/Sismo_Pipeline.log.20240808174630:54`
- artefato de conflito de merge dentro de log historico:
  - `.specs/codebase/arquivos/registros/.bkp/Sismo_Pipeline.log.20240805141037:6`
  - `.specs/codebase/arquivos/registros/.bkp/Sismo_Pipeline.log.20240805141037:1895831`

## Padroes temporais observados

1. **2024-07-31 a 2024-08-03**
   Predominio de execucoes curtas de pre-processamento (`P`) e falhas de
   inicializacao/parametrizacao.

2. **2024-08-05**
   Execucao `PE` de longa duracao conclui com `ok`, salva `eventos.csv` e
   `erros.csv`.

3. **2024-08-06 a 2024-08-08 (janela de aquisicao intensa)**
   Logs gigantes de `E` mostram repeticao de mensagens de metadado de canal e
   erros de finalizacao.

4. **2024-08-26 a 2024-10-10**
   Cresce o uso de fluxo completo (`PERO`, `PEROMT`), com recorrencia de
   falha em `pos_processa.py` por ausencia da coluna `CFT`.

5. **2024-10-14 em diante**
   Aparecem falhas no `rnc` (`Series.append`) e, em execucoes headless, falha
   de backend `Qt5Agg`.

## Correlacao log x estado de codigo (git)

Correlacao feita por `prev_commit` (ultimo commit com data anterior ao timestamp
do log). Destaques:

1. `Sismo_Pipeline.log.20240805141037`
   commit anterior `5b3ee71` (altera `fluxo_sismo.sh`).

2. `Sismo_Pipeline.log.20240806150022`
   commit anterior `922e674` (alteracoes em `fonte/nucleo/fluxo_eventos.py`).

3. `Sismo_Pipeline.log.20240808123655`
   commit anterior `d65a262` (janela de repeticao de testes do pipeline).

4. `Sismo_Pipeline.log.20241008170339`
   commit anterior `44d4d65` (estado estavel longo entre 2024-08-27 e
   2024-10-10).

5. `Sismo_Pipeline.log.20241014090430`
   commit anterior `2c6e2ac` (mudancas em `pos_processa.py` e
   `fluxo_eventos.py`).

## Excecoes finais mais frequentes

1. `TypeError: cannot unpack non-iterable NoneType object` (16)
2. `KeyError: 'Column not found: CFT'` (12)
3. `ImportError: ... backend 'Qt5Agg' ... headless` (8)
4. `AttributeError: 'Series' object has no attribute 'append'` (7)
5. `UnboundLocalError: ... DATA_CLIENT ...` (6)

## Conclusao para a reescrita v2

O historico de logs confirma que o `fluxo_sismo.sh` funciona como orquestrador
de etapas heterogeneas (aquisicao, inferencia, pos-processamento, mapas e
relatorio), com falhas recorrentes concentradas em:

- contrato de dados entre etapas (ex.: coluna `CFT`);
- tratamento de fallback de cliente/metadados;
- dependencias de ambiente (GUI/headless e bibliotecas locais);
- baixa padronizacao de encerramento (`ok` vs `trace` vs `partial`).

Este documento e o anexo CSV formam a base de evidencia para a especificacao da
proxima etapa de refatoracao.
