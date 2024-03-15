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
from obspy.clients import fds

# ClassificadorSismologico
from ProcessarCatalogoSismo import gera_catalogo_event_id
from BaixarFormaOnda import baixar_waveform
from utils import csv2list, cria_sta_dic, list_inventario, delimt, get_inventory_from_xml


# ---------------------------- FUNÇÕES ----------------------------------------
# função main que conterá as chamadas das funções
def main(IDs, network_id, catalog_Client, data_Client, data_Client_bkp):
    catalogo = gera_catalogo_event_id(IDs, network_id, catalog_Client)
    # Constroi o inventario de estações
    inventario = {}
    print(' --> Inventário de Estações:')
    for file in list_inventario:
        # Check if the file is a .txt
        if file.endswith('.txt'):
            txt = file
            print(f' - Arquivo: {txt}')
            inventario = cria_sta_dic('./files/inventario/' + txt, inventario)
        # print(f' - {len(inventario)}')
    inventory = get_inventory_from_xml('./files/inventario/inventario_rsbr.xml',
                                       inventario)
    print(delimt)
    # Baixa a forma de onda
    # print(f' Catalog.events: {catalogo.events}')
    # print(f' Client: {client}')
    # print(f' Inventário: {inventario}')
    baixar_waveform(catalogo.events, data_Client, data_Client_bkp, inventory)
    return catalogo


# ---------------------------- MAIN -------------------------------------------
if __name__ == "__main__":
    print('')
    print(f' - Argumento 1: {sys.argv[1]}')
    print(f' - Argumento 2: {sys.argv[2]}')
    csv_file = sys.argv[1]
    network_id = sys.argv[2]
    mode = "t"  # Supondo que o modo sempre será "t"
    IDs = csv2list(csv_file)
    data_Client_main = fdsn.Client('http://seisarc.sismo.iag.usp.br/')
    data_Client_USP = fdsn.Client('USP')
    data_Client_bkp = fdsn.Client('http://rsbr.on.br:8081/fdsnws/dataselect/1/')
#    if network_id == 'USP':
#        # Servidor MOHO IAG (USP)
#        data_catalog_Client = fdsn.Client('USP')
#    else:
#        # Servidor IPT
#        catalog_Client = fdsn.Client('http://localhost:' + ID_dict[network_id])
#        data_Client = catalog_Client
    catalog_Client = fdsn.Client('http://seisarc.sismo.iag.usp.br')
    data_Client_bkp = fdsn.Client('USP')
    data_Client = fdsn.Client('http://seisarc.sismo.iag.usp.br/')
    print(f' --> Client:\n  {catalog_Client}')
    print(delimt)
    print('')
    print(" --------- Iniciando o ProcessarID.py --------- ")
    main(IDs, network_id, catalog_Client, data_Client, data_Client_bkp)
