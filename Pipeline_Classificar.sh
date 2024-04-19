#!/bin/bash
# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# ./ClassificadorSismologico/Sismo_Pipeline.sh
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.2
# Data: 2024-03-05
# Modificado: 2024-04-10
#

# ----------------------------  DESCRIPTION  -----------------------------------
# Este código recebe uma lista de IDs eventos ou uma data de início e fim e com
# estas informações cria um arquivo event-<CLIENT_ID>.csv com os eventos
# sismicos que ocorreram no intervalo de tempo especificado e foram capturados
# pela rede sismológica. Com este arquivo, segue-se para o passo de aquisição
# das formas de onda e criação dos mapas.

# -------------------------------  USO -----------------------------------------
# Para executar este script, basta rodar o comando abaixo:
# ./Sismo_Pipeline.sh [INICIO] [FIM] [CLIENT_ID]
# ./Sismo_Pipeline.sh [CLIENT_ID] [EVENTS]

# -----------------------------  VARIÁVEIS -------------------------------------
# DEFINE OS PARAMETROS DE CRIAÇÃO DE CATALOGO DE EVENTOS
INICIO=${1:-"2023-01-01"}
FIM=${2:-"2023-01-10"}
DATES="$INICIO $FIM"  # BASEADO EM DATAS

# CATALOGO DE EVENTOS
CATALOG=${1:-"files/catalogo/catalogo-moho.csv"}  # BASEADO EM LISTA DE IDS
# CLIENT_ID
CLIENT_ID=${2:-"moho"}

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
    echo ' -> Executando events_pipeline.py...'
    $PYTHON3 source/core/events_pipeline.py $CATALOG $CLIENT_ID
    echo ''
    echo " Criando arquivos de backup..."
    [[ -f files/events/events.csv ]] &&
        cp files/events/events.csv files/events/.bkp/events.csv.$(date +%Y%m%d%H%M%S)
    [[ -f files/logs/missing_ids/missing_ids.csv ]] &&
        cp files/logs/missing_ids/missing_ids.csv files/logs/missing_ids/.bkp/missing_ids.csv.$(date +%Y%m%d%H%M%S)
    echo " Arquivos de backup criados com sucesso!"
    echo ''
fi

# --------- ETAPA DE GERAR LISTA PARA CLASSIFICAÇÃO ( EVENTO | LABEL ) -----------
PROCESS_PRED=${PROCESS_PRED:-true}
if [ "$PROCESS_PRED" = true ]; then
    # chega se o arquivo de predições já existe, se existir, move para uma pasta de backup
    echo " ---------------- Iniciando o cria_pred.py ---------------------------- "
    $PYTHON3 source/core/gerar_predcsv.py
    echo ''
    echo " Criando arquivos de backup..."
    cp files/logs/predcsv/pred.csv files/logs/predcsv/.bkp/pred.csv.$(date +%Y%m%d%H%M%S)
    echo " Arquivos de backup criados com sucesso!"
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
