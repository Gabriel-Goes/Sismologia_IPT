# -*- coding: utf-8 -*-
# Python 3.10
# ./Classificador_Sismologico/pyscripts/ProcessarID.py


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
from BaixarFormaOnda import baixar_waveform

from utils import csv2list, cria_sta_dic, list_inventario, delimt


# ---------------------------- FUNÇÕES ----------------------------------------
# função main que conterá as chamadas das funções
def main(lista, network_id):
    # Gera o catálogo de eventos por ID
    IDs = csv2list(lista)
    lil_IDs = IDs[:50]
    catalogo, client = gera_catalogo_event_id(lil_IDs, network_id)
    # Constroi o inventario de estações
    inventario = {}
    print(' --> Inventário de Estações:')
    for txt in list_inventario:
        inventario = cria_sta_dic('./files/inventario/' + txt, inventario)
        # print(f' - {len(inventario)}')
    print(delimt)
    # Baixa a forma de onda
    # print(f' Catalog.events: {catalogo.events}')
    # print(f' Client: {client}')
    # print(f' Inventário: {inventario}')
    baixar_waveform(catalogo.events, client, inventario)
    return catalogo


# ---------------------------- MAIN -------------------------------------------
if __name__ == "__main__":
    print('')
    print(f' - Argumento 1: {sys.argv[1]}')
    print(f' - Argumento 2: {sys.argv[2]}')
    csv_file = sys.argv[1]
    network_id = sys.argv[2]
    mode = "t"  # Supondo que o modo sempre será "t"
    print('')
    print(" --------- Iniciando o ProcessarID.py --------- ")
    main(csv_file, network_id)
