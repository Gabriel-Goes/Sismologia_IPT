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
#

# ----------------------------  DESCRIPTION  -----------------------------------
# Este código recebe uma lista de IDs eventos ou uma data de início e fim e com
# estas informações cria um arquivo events.csv com os eventos sísmicos que 
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
# da rede do IAG e do RSBR e criará um arquivo events_$INICIO_$FIM.csv
#
# Caso utilize uma lista de IDs, o script irá adquirir os eventos sísmicos desta
# mesma rede e criará um arquivo events.csv

# -----------------------------  VARIÁVEIS -------------------------------------
# DEFINE OS PARAMETROS DE CRIAÇÃO DE CATALOGO DE EVENTOS
INICIO=${1:-"2023-01-01"}
FIM=${2:-"2023-01-10"}
DATES="$INICIO $FIM"  # BASEADO EM DATAS

# CATALOGO DE EVENTOS
CATALOG=${1:-"files/catalogo/catalogo-moho.csv"}  # BASEADO EM LISTA DE IDS

# ----------------------------- CONSTANTES -------------------------------------
# DEFINE OS DIRETÓRIOS DE TRABALHO
BASE_DIR=$HOME/projetos/ClassificadorSismologico/
cd $BASE_DIR

# DEFINE O DIRETÓRIO DE LOGS
LOG_DIR="files/logs"
LOG_FILE="$LOG_DIR/Sismo_Pipeline.log"
LOG_FILE_BKP="$LOG_DIR/.bkp/$(date +%Y%m%d%H%M%S)_Sismo_Pipeline.log"
mkdir -p files
mkdir -p figures
mkdir -p $LOG_DIR

# CRIA O ARQUIVO DE LOG
mv -f $LOG_FILE $LOG_FILE_BKP
touch "$LOG_FILE"
exec 1> >(tee -a "$LOG_FILE") 2>&1

# DEFINE EXECUTAVEIS
ENERGYFIG="$HOME/lucas_bin/energy_fig.py"
CREATEMAP="$HOME/lucas_bin/make_maps_"$CLIENT_ID".py"
SEISCOMP=${SEISCOMP:-"$HOME/softwares/seiscomp/bin/seiscomp"}
PYTHON3=${PYTHON3:-"$HOME/.pyenv/versions/sismologia/bin/python3"}

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
# CRIANDO CATÁLOGO DE EVENTOS SISMICOS E GERANDO UMA TABELA DE METADADOS DE EVENTOS
PROCESS_EVENTS=${PROCESS_EVENTS:-true}
if [ "$PROCESS_EVENTS" = true ]; then
    echo " Criando arquivos de backup..."
    [[ -f files/events/events.csv ]] &&
        mv files/events/events.csv files/events/.bkp/events.csv.$(date +%Y%m%d%H%M%S)
    [[ -f files/logs/missing_ids.csv ]] &&
        mv files/logs/missing_ids.csv files/logs/.bkp/missing_ids.csv.$(date +%Y%m%d%H%M%S)
    echo " Arquivos de backup criados com sucesso!"
    echo ''
    echo ' -> Executando events_pipeline.py...'
    $PYTHON3 source/core/events_pipeline.py $CATALOG
    echo ''
fi

# --------- ETAPA DE GERAR LISTA PARA CLASSIFICAÇÃO ( EVENTO | LABEL ) -----------
PROCESS_PRED=${PROCESS_PRED:-true}
if [ "$PROCESS_PRED" = true ]; then
    echo " Criando arquivos de backup..."
    cp files/predcsv/pred.csv files/predcsv/.bkp/pred.csv.$(date +%Y%m%d%H%M%S)
    echo " Arquivos de backup criados com sucesso!"
    echo ''
    # checa se o arquivo de predições já existe, se existir, move para uma pasta de backup
    echo " ---------------- INICIANDO CORE/GERAR_PREDCSV.PY ---------------------------- "
    $PYTHON3 source/core/gerar_predcsv.py
    echo ''
    # CHECA SE DEVE SER PREPROCESSADO
    PREPROCESS=${PREPROCESS:-true}
    if [ "$PREPROCESS" = true ]; then
        cp files/predcsv/pred_commercial.csv files/predcsv/.bkp/pred_commercial.csv.$(date +%Y%m%d%H%M%S)
        cp files/predcsv/pred_no_commercial.csv files/predcsv/.bkp/pred_no_commercial.csv.$(date +%Y%m%d%H%M%S)
        echo " -------------- INICIANDO O DATA_ANALYSIS/PREPROCESS.PY -------------------- "
        $PYTHON3 source/data_analysis/pre_process.py
        echo ''
    fi
fi


# ------------------------- ETAPA DE PREDIÇÃO  ----------------------------------
PREDICT=${PREDICT:-true}
if [ "$PREDICT" = true ]; then
    DIR_PROJETO="$HOME/projetos/ClassificadorSismologico/"
    NOME_TERM="DOCKER" # Use underscores no lugar de espaços
    COMMAND='docker run -it --rm -v $HOME/projetos:/app discrim:0.1.0'
    COMMAND_2='export CS_files=ClassificadorSismologico/files; \
python ./discrimination_eq_q/run.py \
    --data_dir ClassificadorSismologico/files/mseed \
    --spectro_dir ClassificadorSismologico/files/spectro \
    --model discrimination_eq_q/model/model_2021354T1554.h5 \
    --output_dir ClassificadorSismologico/files/output/no_commercial \
    --csv_dir ClassificadorSismologico/files/predcsv/pred_no_commercial.csv \
    --valid'
    COMMAND_3='export CS_files=ClassificadorSismologico/files; \
python ./discrimination_eq_q/run.py \
    --data_dir ClassificadorSismologico/files/mseed \
    --spectro_dir ClassificadorSismologico/files/spectro \
    --model discrimination_eq_q/model/model_2021354T1554.h5 \
    --output_dir ClassificadorSismologico/files/output/commercial \
    --csv_dir ClassificadorSismologico/files/predcsv/pred_commercial.csv \
    --valid'

    echo " ----------------- INICIANDO O PREDICT.PY ---------------------------- "
    i3-msg "workspace 5"
    alacritty -e bash -c "tmux new-session -d -s $NOME_TERM -c $DIR_PROJETO && \
    tmux send-keys -t $NOME_TERM 'cd $DIR_PROJETO' C-m && \
    tmux send-keys -t $NOME_TERM '$COMMAND' C-m && \
    tmux send-keys -t $NOME_TERM \"$COMMAND_2\" C-m && \
    tmux send-keys -t $NOME_TERM \"$COMMAND_3\" C-m && \
    tmux attach-session -t $NOME_TERM"
    echo ''
fi

# ------------------------- ETAPA DE GERAR MAPAS  -----------------------------
# Condicionalmente executa partes do script
PROCESS_MAPS=${PROCESS_MAPS:-false}
if [ "$PROCESS_MAPS" = true ]; then
    # Executa etapa de processamento de mapas
    echo " -------------- Processo de criação de mapas iniciado ------------------"
    # Checa se o arquivo de eventos existe e se é vazio
    if [ -f "files/events/events-*.csv" ]; then
        echo " -> Executando make_maps.py..."
        $PYTHON3 $CREATEMAP $EVENTS
        mv $EVENTS files/
        mv *png figures
    else
        echo "events.csv est\u00e1 vazio"
    fi
    for i in $EVENTS
        do
            echo $i
            $PYTHON3 $CREATEMAP $i
            mv $i files/
            mv *png figures
    done
    echo ''
    echo " Criando arquivos de backup..."
    echo " Arquivos de backup criados com sucesso!"
    echo ''
fi

# ----------------- ETAPA DE GERAR FIGURAS DE ENERGIA  ------------------------
PROCESS_ENERGY=${PROCESS_ENERGY:-false}
if [ "$PROCESS_ENERGY" = true ]; then
    # Executa etapa de processamento de energia
    echo " ----------------- Iniciando o energy_fig.py ---------------------------- "
    echo "Creating energy plots..."
    $PYTHON $ENERGYFIG $OUTPUT
    echo "Cleaning up..."
    mv events*.csv files/
    echo ''
    echo " Criando arquivos de backup..."
    echo " Arquivos de backup criados com sucesso!"
    echo ''
fi

echo $DELIMT2
echo "                        Fim do Pipeline                                 "
echo $DELIMT2
echo ''
