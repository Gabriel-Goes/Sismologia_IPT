# Estado atual do sistema (commit `9c3c01b`)

## 1) Objetivo desta etapa

Este documento registra o estado tecnico atual do projeto para iniciar a
refatoracao com rastreabilidade. O foco foi **somente leitura** dos arquivos
`.py`, `.sh`, `.md` e `.txt`, sem alteracao de codigo.

## 2) Snapshot do repositorio

- Branch atual: `ipt` (tracking `origin/ipt`)
- Commit atual (HEAD): `9c3c01be31b67e7711d9a46ce762782d629e2ea6`
- Mensagem: `Commit: Refatoração de código iniciada. Iniciando por documentação do estado atual.`
- Data do commit: `2026-02-09 20:47:58 -0300`
- Arvore de trabalho: limpa no momento da leitura

## 3) Escopo lido

- Scripts Python: `55`
- Scripts shell: `12`
- Arquivos Markdown/TXT: `28`

Inventario detalhado: `documentação/inventario_arquivos.md`.

## 4) Visao macro do fluxo atual

Pipeline principal observado:

1. `fluxo_sismo.sh` recebe catalogo e flags de execucao.
2. `fonte/analise_dados/pre_processa.py` trata e filtra catalogo.
3. `fonte/nucleo/fluxo_eventos.py` consulta eventos FDSN, baixa formas de onda e monta `arquivos/eventos/eventos.csv`.
4. `fonte/rnc/run.py` chama:
   - `fonte/rnc/data_process.py` para extracao de espectrogramas (`.npy`);
   - `fonte/rnc/prediction.py` para inferencia com modelo `.h5`.
5. `fonte/analise_dados/pos_processa.py` calcula metricas e gera graficos.
6. Blocos opcionais:
   - `fonte/analise_dados/gera_mapas.py` para mapas com `pygmt`;
   - scripts em `fonte/relatorio-sismologia/pyscripts/` para montar trechos LaTeX e relatorios.

## 5) Modulos e responsabilidades

### 5.1 Orquestracao shell

- `fluxo_sismo.sh`
  - Script central do pipeline.
  - Flags: `--eventos`, `--pre`, `--predict`, `--pos`, `--maps`, `--report`, `--test`.
  - Chama diretamente os modulos Python de preprocessamento, aquisicao, predicao,
    pos-processamento e relatorio.
  - Escreve log em `arquivos/registros/Sismo_Pipeline.log`.
- `farejador.sh`
  - Executa interface local `fonte/interface/farejador.py`.
- `plugin.sh`
  - Copia plugin QGIS para pasta de plugins e abre o QGIS.
- `config/instalar.sh`
  - Script de bootstrap de ambiente (pyenv, virtualenv, dependencia, install `-e .`).

Observacoes tecnicas:

- Existem caminhos absolutos e dependencias de ambiente local em varios scripts.
- O pipeline mistura passos de ciencia de dados, aquisicao, GUI e LaTeX em uma
  unica orquestracao.

### 5.2 Aquisição e pre-processamento de dados sismicos

- `fonte/analise_dados/pre_processa.py`
  - Le catalogo em `arquivos/catalogo/`.
  - Filtra por data e por geometria (dentro/entorno do Brasil via geopandas).
  - Gera histogramas por hora e profundidade.
  - Salva catalogo filtrado (`*_filtrado.csv`).
  - Usa `matplotlib.use('Agg')` (modo sem GUI).
- `fonte/nucleo/fluxo_eventos.py`
  - Busca metadados e eventos em servidores FDSN (principal e backup).
  - Para picks P, calcula distancia epicentral, baixa janelas mseed e grava em
    `arquivos/mseed/<evento>/`.
  - Gera:
    - `arquivos/eventos/eventos.csv`
    - `arquivos/eventos/erros.csv`
    - `arquivos/registros/id_faltantes.csv`
- `fonte/nucleo/utils.py`
  - Constantes de categorias, diretorios e utilitarios (`csv2list`, `DualOutput`).
- `fonte/nucleo/iag/exporter.py` e `fonte/nucleo/iag/getEventData.py`
  - Scripts auxiliares/legados de exportacao e download via FDSN.

Observacoes tecnicas:

- Acoplamento alto a arquivos CSV em caminhos fixos.
- Mistura de regras de negocio, IO e logging em funcoes longas.

### 5.3 Rede neural e inferencia

- `fonte/rnc/data_process.py`
  - Funcoes para FFT, janelamento, decimacao para 100 Hz e extracao de
    espectrogramas por pick.
- `fonte/rnc/prediction.py`
  - Carrega modelo Keras `.h5`, infere por pick e agrega por evento.
  - Salva resultado em `arquivos/resultados/predito.csv`.
- `fonte/rnc/run.py`
  - Entrada CLI para pipeline de inferencia.
  - Le `arquivos/eventos/eventos.csv`, gera espectros e executa classificacao.
- `fonte/rnc/train.py`
  - Script de treinamento de arquitetura CNN + metadados.
  - Salva `model_with_metadata.h5`.

Observacoes tecnicas:

- Dependencia forte de estrutura de pastas local.
- `train.py` esta no formato de script executado por efeito colateral (sem
  funcoes/classes).

### 5.4 Pos-processamento e metricas

- `fonte/analise_dados/pos_processa.py`
  - Arquivo monolitico (~1800 linhas) com calculo de SNR, classificacoes por
    faixa, curvas de recall e dezenas de graficos.
  - Separa analise por horario comercial e nao-comercial.
  - Salva resultados analisados finais em `arquivos/resultados/`.
- `fonte/analise_dados/testa_filtros.py`
  - Ferramentas para avaliar combinacoes de filtro e janelas P/S/noise.
- `fonte/analise_dados/gera_mapas.py`
  - Gera mapas de probabilidade e por macrorregiao (PyGMT + GeoPandas).

Observacoes tecnicas:

- Concentra muita responsabilidade em um unico modulo (`pos_processa.py`).
- Parte dos plots ainda usa `show()` em fluxos de batch.

### 5.5 Interface e plugin QGIS

- `fonte/interface/farejador.py`
  - Aplicacao PyQt standalone para navegar eventos, picks e espectrogramas.
- Pacote plugin `fonte/interface/farejadorsismo/`
  - `farejadorsismo.py`: bootstrap do plugin no QGIS.
  - `farejadorsismo_dockwidget.py`: logica da dock com leitura de CSV,
    camada em mapa e visualizacao de waveforms/espectros.
  - `farejadorsismo_dockwidget_base.py`: classe gerada por `pyuic5`.
  - `resources.py`: arquivo gerado por `pyrcc5`.
  - `test/`: suite base de testes de plugin QGIS.

Observacoes tecnicas:

- Mistura de arquivos gerados automaticamente com logica manual.
- Scripts de build/deploy (`Makefile`, `pb_tool.cfg`, scripts de traducao)
  ainda com caminhos fixos de ambiente.

### 5.6 Relatorios LaTeX

- `fonte/relatorio-sismologia/pyscripts/`
  - Scripts para gerar trechos `.tex` (mapas, tabelas, figuras, completude).
  - Grande repeticao de codigo entre `tabela*.py`.
  - Varias referencias para caminhos absolutos externos ao projeto atual.
- `fonte/relatorio-sismologia/tex/*/logs/*.txt`
  - Logs de compilacao LaTeX (inclusive execucoes com erro de classe/pacote em
    alguns cenarios).

## 6) Documentos `.md` e `.txt` relevantes

- `LEIAME.md`
  - Documento principal de uso/objetivo do projeto.
- `fonte/rnc/README.md`
  - Referencia do projeto original de discriminacao de eventos.
- `anotações.txt`
  - Lista manual de eventos e agrupamentos por probabilidade.
- `test.txt`
  - Registro textual de execucoes e erros (inclui erro de backend Qt/Matplotlib em ambiente headless).
- `fonte/interface/farejadorsismo/README.txt` e `metadata.txt`
  - Arquivos de template de plugin QGIS.
- `fonte/relatorio-sismologia/README.md` e docs em `docs/`
  - Material de apoio para estrutura de relatorios LaTeX.

## 7) Diagnostico tecnico inicial (base para refatoracao)

1. **Acoplamento por caminho absoluto**: varios scripts dependem de
   `~/projetos/...` ou caminhos de maquinas antigas (`/home/ipt/...`).
2. **Modulos monoliticos**: `pos_processa.py` e `fluxo_eventos.py` concentram
   muitas responsabilidades.
3. **Duplicacao de codigo**: familia `tabela*.py` no bloco de relatorio.
4. **Baixa separacao de camadas**: IO de arquivos, logica de negocio e plot
   misturados.
5. **Padrao de entrada/saida heterogeneo**: uso simultaneo de CSVs parciais
   em multiplas pastas sem contrato unico.
6. **Scripts legados e arquivos gerados** convivendo com codigo ativo,
   dificultando manutencao.
7. **Dependencia de GUI em partes do fluxo** (QGIS, PyQt, `show()`), o que
   dificulta execucao headless/CI.

## 8) Proximo passo recomendado para a refatoracao

1. Definir contrato unico de dados intermediarios (schema de eventos/picks).
2. Quebrar pipeline em modulos pequenos com interfaces explicitas:
   - ingestao
   - preprocessamento
   - inferencia
   - avaliacao
   - relatorio
3. Isolar configuracao de caminho/credenciais em arquivo unico (`.env` + YAML).
4. Separar scripts gerados/legados em area de arquivo historico.
5. Introduzir testes de regressao para garantir equivalencia de resultados
   antes de alterar algoritmos.

