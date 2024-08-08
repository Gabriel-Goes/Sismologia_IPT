#!/bin/bash
# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# ./ClassificadorSismologico/fluxo_sismo.sh
# Autor: Gabriel Góes Rocha de Lima
# Modificado do código de Lucas Schirbel & Marcelo Bianchi
# Versão: 0.3.1
# Data: 2024-03-05
# Modificado: 2024-07-31

# ----------------------------  DESCRIÇÃO  -----------------------------------
# Este código recebe uma lista de IDs eventos ou uma data de início e fim e com
# estas informações cria um arquivo eventos.csv com os eventos sísmicos que
# ocorreram no intervalo de tempo especificado ou com os IDs presentes na lista
# passada e foram capturados pela rede sismológica. Com este arquivo, segue-se
# para o passo de aquisição das formas de onda e classificação.

# -------------------------------  USO -----------------------------------------
# Passando uma lista de IDs de eventos sísmicos:
#       Sismo_Pipeline.sh catalogo.csv
#
# Caso utilize uma lista de IDs, o script irá adquirir os eventos sísmicos da
# rede seisarc e criará um arquivo eventos.csv

# -----------------------------  VARIÁVEIS ------------------------------------
EVENTS=False
TREATCATALOG=False
PREDICT=False
POSPROCESS=False
MAPS=False
REPORT=False
TEST=False

# ------------------------- PARSE ARGUMENTOS ----------------------------------
if [ $# -eq 0 ]; then # Não está funcionando. ## Deve configurar tudo como true caso não seja passado argumentos ao ./flusho_sismo.sh, porém, para rodar o bash, é necessário passar o nome do arquivo de catalogo_MÊS.csv, isso impede de funcionar.
    EVENTS=True
    TREATCATALOG=True
    PREDICT=True
    POSPROCESS=True
    MAPS=True
    REPORT=True
    TEST=False
else
    if [ -f  "./arquivos/catalogo/$1" ]; then
        CATALOG=$(basename "$1")
        echo "Catalogo: $CATALOG"
        shift
    else
        echo "Erro: Arquivo $1 não encontrado!"
        exit 1
    fi
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                echo "Uso: $0 [opções] [catalogo.csv]"
                echo "Opções:"
                echo "  --eventos, -e:    Executa a aquisição de eventos sísmicos"
                echo "  --pre, -pe:       Executa o tratamento do catálogo"
                echo "  --predict, -pr:   Executa o script de predição"
                echo "  --pos, -po:       Executa o pós-processamento"
                echo "  --maps, -m:       Executa a geração de mapas"
                echo "  --test, -t:       Executa um bach de testes com 500 eventos"
                echo "  --report, -r:     Executa a geração de relatórios"
                exit 0
                ;;
            --eventos|-e)
                EVENTS=True
                ;;
            --pre|-pe)
                TREATCATALOG=True
                ;;
            --predict|-pr)
                PREDICT=True
                ;;
            --pos|-po)
                POSPROCESS=True
                ;;
            --maps|-m)
                MAPS=True
                ;;
            --test|-t)
                TEST=True
                ;;
            --report|-r)
                REPORT=True
                ;;
            *)
                echo "Opção inválida: $1"
                exit 1
                ;;
        esac
        shift
    done
fi

# -----------------------------  VARIÁVEIS -------------------------------------
EVENTS=${EVENTS:-False}
TREATCATALOG=${TREATCATALOG:-True}
PREDICT=${PREDICT:-False}
POSPROCESS=${POSPROCESS:-False}
MAPS=${MAPS:-False}
REPORT=${REPORT:-False}

# ----------------------------- CONSTANTES -------------------------------------
set -e
# DEFINE OS DIRETÓRIOS DE TRABALHO
BASE_DIR=$HOME/projetos/ClassificadorSismologico/
pushd $BASE_DIR

# DEFINE O DIRETÓRIO DE LOGS
LOG_DIR="arquivos/registros"
LOG_FILE="$LOG_DIR/Sismo_Pipeline.log"
mkdir -p arquivos/$LOG_DIR

if [ -f $LOG_FILE ]; then
    mv $LOG_FILE $LOG_DIR/.bkp/Sismo_Pipeline.log.$(date +%Y%m%d%H%M%S)
    touch "$LOG_FILE"
fi

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

# PRINT ARGUMENTS RECEIVED AND DEFAULTS
echo "Argumentos recebidos:"
echo "  Catalogo: $CATALOG"
echo "  EVENTS: $EVENTS"
echo "  TREATCATALOG: $TREATCATALOG"            # Código para ajuda
echo "  PREDICT: $PREDICT"
echo "  POSPROCESS: $POSPROCESS"
echo "  MAPS: $MAPS"
echo "  REPORT: $REPORT"
echo "  TEST: $TEST"
echo ''

# ------------------------- ETAPA DE AQUISIÇÃO DE DADOS  ----------------------
if [ "$TREATCATALOG" = True ]; then
        echo ''
        echo " -------------- INICIANDO O TRATAMENTO -------------------- "
        echo " Tratando $CATALOG..."
        python fonte/analise_dados/pre_processa.py -c $CATALOG
fi

if [ "$EVENTS" = True ]; then
    echo " Criando arquivos de backup..."
    [[ -f /eventos/eventos.csv ]] &&
        mv arquivos/eventos/eventos.csv arquivos/eventos/.bkp/eventos.csv.$(date +%Y%m%d%H%M%S)
    [[ -f arquivos/registros/ids_faltantes.csv ]] &&
        mv arquivos/registros/ids_faltantes.csv arquivos/registros/.bkp/ids_faltantes.csv.$(date +%Y%m%d%H%M%S)
    echo " Arquivos de backup criados com sucesso!"
    echo ''
    echo ' -> Executando fluxo_eventos.py...'
    echo $CATALOG
    python fonte/nucleo/fluxo_eventos.py $CATALOG $TEST
    echo ''
fi

# ------------------------- ETAPA DE PREDIÇÃO  ----------------------------------
if [ "$PREDICT" = True ]; then
    NOME_TERM="Predict"
    COMMAND='pushd /home/ipt/projetos/ClassificadorSismologico; \
        python fonte/rnc/run.py'
    echo " ----------------- INICIANDO O PREDICT.PY ---------------------------- "
    i3-msg 'workspace 2'
    alacritty -e bash -c "tmux new-session -d -s $NOME_TERM; \
    tmux send-keys -t $NOME_TERM \"$COMMAND\" C-m; \
    tmux attach -t $NOME_TERM"
    echo ''
fi

# --------- ETAPA DE GERAR GRAFICOS E ANÁLISES -----------
if [ "$POSPROCESS" = True ]; then
    echo " ---------------- INICIANDO DATA_ANALYSIS/POSPROCESS.PY ---------------------------- "
    python fonte/analise_dados/pos_processa.py
    echo ''
fi

# ------------------------- ETAPA DE GERAR MAPAS  -----------------------------
# Condicionalmente executa partes do script
if [ "$MAPS" = True ]; then
    echo " -------------- Processo de criação de mapas iniciado ------------------"
    # Checa se o arquivo de eventos existe e se é vazio
    if [ -f "arquivos/output/no_commercial/df_nc_pos.csv" ]; then
        echo " -> Executando make_maps.py..."
        python fonte/analise_dados/gera_mapas.py
    fi
    echo ''
fi

# ----------------- ETAPA DE GERAR RELATORIOS ------------------------
if [ "$REPORT" = True ]; then
    echo " ----------------- Iniciando o pdflatex .tex ---------------------------- "
    python fonte/relatorio-sismologia/pyscripts/figures.py --path 'pre_processa'
    python fonte/relatorio-sismologia/pyscripts/figures.py --path 'pos_processa'
    python fonte/relatorio-sismologia/pyscripts/mapa.py
    pushd fonte/relatorio-sismologia
    pdflatex -output-directory=$HOME/projetos/ClassificadorSismologico/arquivos/resultados/relatorios relatorio_preditivo.tex
    popd
fi

echo $DELIMT2
echo "                        Fim do Pipeline                                 "
echo $DELIMT2
echo ''
popd
