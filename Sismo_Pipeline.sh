#!/bin/bash
# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# ./ClassificadorSismologico/Sismo_Pipeline.sh
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.1
# Data: 2024-03-05
#

# ----------------------------  DESCRIPTION  -----------------------------------
# Este código recebe uma data de início e uma data de fim e um CLIENT_ID de rede sismo
# lógica. Com estas informações cria um arquivo event-<CLIENT_ID>.csv com os eventos sismicos
# que ocorreram no intervalo de tempo especificado e foram capturados pela rede sismológica.
# Com este arquivo, segue-se para o passo de aquisição das formas de onda e criação dos mapas.

# ----------------------------  USAGE  -----------------------------------------
# Para executar este script, basta rodar o comando abaixo:
# ./Sismo_Pipeline.sh [INICIO] [FIM] [CLIENT_ID]

# Se não escolher nada, estes valores padrão serão usados:
INICIO=${1:-"2023-01-01"}
FIM=${2:-"2023-01-10"}
DATES=${4:-"$INICIO $FIM"}

# Define um diretório base, todas as funções são relativas a este diretório base,
BASE_DIR=${BASE_DIR:-"$HOME/projetos/ClassificadorSismologico"}
MOHO_CATALOG="$BASE_DIR/files/catalogo/catalogo-moho.csv"
cd $BASE_DIR
mkdir -p files
mkdir -p figures

EVENTS=$(find files/ -maxdepth 1 -name "events-*.csv")
ENERGYFIG="$HOME/lucas_bin/energy_fig.py"
CREATEMAP="$HOME/lucas_bin/make_maps_"$CLIENT_ID".py"

# PYTHON3=${PYTHON3:-"$HOME/.config/geo/bin/python3"}
# SEISCOMP=${SEISCOMP:-"$HOME/softwares/seiscomp/bin/seiscomp"}
PYTHON3=${PYTHON3:-"$HOME/.pyenv/versions/sismologia/bin/python3"}
SEISCOMP=${SEISCOMP:-"/opt/seiscomp/bin/seiscomp"}
SISMOLOGIA=${SISMOLOGIA:-"$HOME/projetos/ClassificadorSismologico"}
DELIMT1='########################################################################'

# Define o diretório de logs e cria o arquivo de log
LOG_DIR="$BASE_DIR/logs"
mkdir -p $LOG_DIR
LOG_FILE="$LOG_DIR/$(date +%Y%m%d%H%M%S)_Sismo_Pipeline.log"
touch "$LOG_FILE"
exec 1> >(tee -a "$LOG_FILE") 2>&1


# ------------------------- INICIO DO PIPELINE  ------------------------------
echo ''
echo $DELIMT1
echo " ---------------- Iniciando do Pipeline --------------------------------"
echo ''

# ------------------------- ETAPA DE AQUISIÇÃO DE DADOS  ----------------------
# ---- CRIANDO CATÁLOGO DE EVENTOS SISMICOS ----
PROCESSAR_SISMOS=${PROCESSAR_SISMOS:-true}
if [ "$PROCESSAR_SISMOS" = true ]; then
    echo ' -> Executando ProcessarDadosSismologicos.py...'
    $SEISCOMP exec $PYTHON3 $SISMOLOGIA/source/Core/ProcessarDadosSismologicos.py $MOHO_CATALOG $CLIENT_ID
fi

# ------------------------- ETAPA DE GERAR MAPAS  -----------------------------
# Condicionalmente executa partes do script
PROCESS_MAPS=${PROCESS_MAPS:-false}
if [ "$PROCESS_MAPS" = true ]; then
    # Executa etapa de processamento de mapas
    echo " -------------- Processo de criação de mapas iniciado ------------------"
    # Checa se o arquivo de eventos existe e se é vazio
    if [ -f "files/events-*.csv" ]; then
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
fi

# --------- ETAPA DE GERAR LISTA PARA CLASSIFICAÇÃO ( EVENTO | LABEL ) -----------
PROCESS_PRED=${PROCESS_PRED:-false}
if [ "$PROCESS_PRED" = true ]; then
    # chega se o arquivo de predições já existe, se existir, move para uma pasta de backup
    if [ -f "files/pred-*.csv" ]; then
        mv files/pred.csv files/outros_pred/
    fi
    echo " ---------------- Iniciando o cria_pred.py ---------------------------- "
    $PYTHON3 pyscripts/Gerar_predcsv.py
fi

echo ''
echo " ---------------------- Fim do Pipeline --------------------------------"
echo $DELIMT1
echo ''
