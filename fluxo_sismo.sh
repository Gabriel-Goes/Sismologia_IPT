#!/bin/bash
# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# ./ClassificadorSismologico/Sismo_Pipeline.sh
# Autor: Gabriel Góes Rocha de Lima
# Modificado do código de Lucas Schirbel
# Versão: 0.2
# Data: 2024-03-05
# Modificado: 2024-04-10
#

# ----------------------------  DESCRIÇÃO  -----------------------------------
# Este código recebe uma lista de IDs eventos ou uma data de início e fim e com
# estas informações cria um arquivo eventos.csv com os eventos sísmicos que 
# ocorreram no intervalo de tempo especificado ou presentes na lista passada e
# foram capturados pela rede sismológica. Com este arquivo, segue-se para o
# passo de aquisição das formas de onda e classificação.

# -------------------------------  USO -----------------------------------------
# Existem duas formas de execução:
#   - Passando uma lista de IDs de eventos sísmicos:
#       Sismo_Pipeline.sh catalogo.csv
#
#   - Passando uma data de início e fim:
#    Sismo_Pipeline.sh 2023-01-01 2023-01-10
#
#
# Caso utilize datas para a execução, o script irá adquirir os eventos sísmicos
# da rede do IAG e do RSBR e criará um arquivo eventos_$INICIO_$FIM.csv
#
# Caso utilize uma lista de IDs, o script irá adquirir os eventos sísmicos desta
# mesma rede e criará um arquivo eventos.csv

# -----------------------------  VARIÁVEIS -------------------------------------

CATALOG=${1:-"Catalog.csv"}
EVENTS=${EVENTS:-true}
TREATCATALOG=${TREATCATALOG:-true}
TREATEVENTS=${TREATEVENTS:-false}
PREDICT=${PREDICT:-false}
POSPROCESS=${POSPROCESS:-false}
MAPS=${MAPS:-false}
REPORT=${REPORT:-false}

# ----------------------------- CONSTANTES -------------------------------------
# DEFINE OS DIRETÓRIOS DE TRABALHO
BASE_DIR=$HOME/projetos/ClassificadorSismologico/
cd $BASE_DIR

# DEFINE O DIRETÓRIO DE LOGS
LOG_DIR="arquivos/registros"
LOG_FILE="$LOG_DIR/Sismo_Pipeline.log"
LOG_FILE_BKP="$LOG_DIR/.bkp/$(date +%Y%m%d%H%M%S)_Sismo_Pipeline.log"
mkdir -p arquivos
mkdir -p $LOG_DIR

# CRIA O ARQUIVO DE LOG
mv -f $LOG_FILE $LOG_FILE_BKP
touch "$LOG_FILE"
exec 1> >(tee -a "$LOG_FILE") 2>&1

# DEFINE DELIMITADORES PARA LOGS
DELIMT1='########################################################################'
DELIMT2='========================================================================'

# ---------------------------- INICIO DO PIPELINE  ------------------------------
echo ''
echo $DELIMT2
echo "                       Iniciando do Pipeline                         "
echo $DELIMT2
echo ''

# ------------------------- ETAPA DE AQUISIÇÃO DE DADOS  ----------------------
if [ "$EVENTS" = true ]; then
    echo " Criando arquivos de backup..."
    [[ -f /eventos/eventos.csv ]] &&
        mv arquivos/eventos/eventos.csv arquivos/eventos/.bkp/eventos.csv.$(date +%Y%m%d%H%M%S)
    [[ -f arquivos/registros/missing_ids.csv ]] &&
        mv arquivos/registros/missing_ids.csv arquivos/registros/.bkp/missing_ids.csv.$(date +%Y%m%d%H%M%S)
    echo " Arquivos de backup criados com sucesso!"
    echo ''
    if [ "$TREATCATALOG" = true ]; then
        echo ''
        echo " -------------- INICIANDO O TRATAMENTO -------------------- "
        echo " Tratando $CATALOG..."
        python fonte/analise_dados/pre_processa.py -c $CATALOG -a -p
        echo ''
        echo ' -> Executando fluxo_eventos.py...'
        python fonte/nucleo/fluxo_eventos.py $CATALOG'_treated.csv'
        echo ''
    else
        echo " -> Executando fluxo_eventos.py..."
        python fonte/nucleo/fluxo_eventos.py $CATALOG
        echo ''
    fi
fi

# --------- ETAPA DE GERAR LISTA PARA CLASSIFICAÇÃO ( EVENTO | LABEL ) -----------
if [ "$TREATEVENTS" = true ]; then
    echo " Criando arquivos de backup..."
    cp arquivos/predcsv/pred.csv arquivos/predcsv/.bkp/pred.csv.$(date +%Y%m%d%H%M%S)
    cp arquivos/predcsv/pred_commercial.csv arquivos/predcsv/.bkp/pred_commercial.csv.$(date +%Y%m%d%H%M%S)
    cp arquivos/predcsv/pred_no_commercial.csv arquivos/predcsv/.bkp/pred_no_commercial.csv.$(date +%Y%m%d%H%M%S)
    echo " Arquivos de backup criados com sucesso!"
    echo ''
    echo " -------------- INICIANDO O DATA_ANALYSIS/PREPROCESS.PY -------------------- "
    python fonte/analise_dados/pre_processa.py
    echo ''
fi

# ------------------------- ETAPA DE PREDIÇÃO  ----------------------------------
if [ "$PREDICT" = true ]; then
    NOME_TERM="DOCKER"
    COMMAND='docker run -it --rm -v $HOME/projetos:/app discrim:0.1.0'
    COMMAND_2='python ClassificadorSismologico/fonte/cnn/run.py \
               --output_dir no_commercial \
               --predcsv pred_no_commercial.csv \
               --valid'
    COMMAND_3='python ClassificadorSismologico/fonte/cnn/run.py \
               --output_dir commercial \
               --predcsv pred_commercial.csv \
               --valid'
    echo " ----------------- INICIANDO O PREDICT.PY ---------------------------- "
    i3-msg 'workspace 9'
    alacritty -e bash -c "tmux new-session -d -s $NOME_TERM; \
    tmux send-keys -t $NOME_TERM \"$COMMAND\" C-m; \
    tmux send-keys -t $NOME_TERM \"$COMMAND_2\" C-m; \
    tmux send-keys -t $NOME_TERM \"$COMMAND_3\" C-m; \
    tmux attach -t $NOME_TERM"
    echo ''
fi

# --------- ETAPA DE GERAR GRAFICOS E ANÁLISES -----------
if [ "$POSPROCESS" = true ]; then
    echo " ---------------- INICIANDO DATA_ANALYSIS/POSPROCESS.PY ---------------------------- "
    python fonte/analise_dados/pos_processa.py
    echo ''
fi

# ------------------------- ETAPA DE GERAR MAPAS  -----------------------------
# Condicionalmente executa partes do script
if [ "$MAPS" = true ]; then
    echo " -------------- Processo de criação de mapas iniciado ------------------"
    # Checa se o arquivo de eventos existe e se é vazio
    if [ -f "arquivos/output/no_commercial/df_nc_pos.csv" ]; then
        echo " -> Executando make_maps.py..."
        python fonte/analise_dados/gera_mapas.py
    fi
    echo ''
fi

# ----------------- ETAPA DE GERAR RELATORIOS ------------------------
if [ "$REPORT" = true ]; then
    echo " ----------------- Iniciando o pdflatex .tex ---------------------------- "
    python fonte/relatorios-relatorios-sismologia/tex/relatorio_preditivo/python/figures.py
    python fonte/relatorios-relatorios-sismologia/tex/relatorio_preditivo/python/mapa.py
    pushd fonte/relatorios-relatorios-sismologia
    pdflatex -output-directory=$HOME/projetos/ClassificadorSismologico/arquivos/relatorios/ relatorio_preditivo.tex 
    popd
fi

echo $DELIMT2
echo "                        Fim do Pipeline                                 "
echo $DELIMT2
echo ''
