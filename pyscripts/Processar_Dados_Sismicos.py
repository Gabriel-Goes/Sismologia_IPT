# -*- coding: utf-8 -*-
# Python 3.10
# ./Classificador_Sismologico/pyscripts/Processar_Dados_Sismicos.py


# ----------------------------  DESCRIPTION  -----------------------------------
# Script para processar dados sismicos
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.1
# Data: 2024-02-27

# Função para executar os scripts de processamento de dados sismicos
# Primeira função a ser chamada é:
# - Gerar Catálogo de Eventos Sísmicos

# ----------------------------  IMPORTS   -------------------------------------
import sys

# ClassificadorSismologico
from ProcessarCatalogoSismo import gera_catalogo_event_id

from utils import csv2list


# ---------------------------- FUNÇÕES ----------------------------------------
# função main que conterá as chamadas das funções
def main(network_id, mode, start_time=False, end_time=False):
    IDs = csv2list('./files/catalogo-moho.csv')
    catalogo = gera_catalogo_event_id(IDs, network_id)
    print(catalogo.events[0].picks[0].waveform_id)
    return catalogo


# ---------------------------- MAIN -------------------------------------------
if __name__ == "__main__":
    print('')
    print(f' - Argumento 1: {sys.argv[1]}')
    print(f' - Argumento 2: {sys.argv[2]}')
    print(f' - Argumento 3: {sys.argv[3]}')
    ta = sys.argv[1]
    te = sys.argv[2]
    ID = sys.argv[3]
    mode = "t"  # Supondo que o modo sempre será "t"
    print('')
    print(" ---------  --------- ")
    main(ta, te, ID, mode)
