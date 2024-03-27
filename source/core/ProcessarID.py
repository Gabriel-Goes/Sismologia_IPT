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
from obspy.clients import fdsn

# ClassificadorSismologico
from ProcessarCatalogoSismo import gera_catalogo_event_id
from BaixarFormaOnda import iterate_events
from utils import csv2list, cria_sta_dic, list_inventario, delimt, get_inventory_from_xml, DualOutput


# ---------------------------- FUNÇÕES ----------------------------------------
# função main que conterá as chamadas das funções
def main(IDs, data_Client, data_Client_bkp):
    sys.stdout = DualOutput("files/logs/iterate_events.txt")
    catalogo, missing_ids = gera_catalogo_event_id(IDs[:-1], data_Client, data_Client_bkp)

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
    inventory = get_inventory_from_xml('files/inventario/inventario_rsbr.xml',
                                       inventario)
    print(delimt)
    # Baixa a forma de onda
    iterate_events(catalogo.events, data_Client, data_Client_bkp, inventory,
                   baixar=True)

    # Save missing_ids list to csv file
    with open('missing_ids.csv', 'w') as f:
        for item in missing_ids:
            f.write("%s\n" % item)
    return catalogo, missing_ids


# ---------------------------- MAIN -------------------------------------------
if __name__ == "__main__":
    print('')
    print(f' - Argumento 1: {sys.argv[1]}')
    moho_catalog_csv = sys.argv[1]
    IDs = csv2list(moho_catalog_csv)
    data_Client = fdsn.Client('http://seisarc.sismo.iag.usp.br/')
    data_Client_bkp = fdsn.Client('http://rsbr.on.br:8081/fdsnws/dataselect/1/')
    print(f' --> Client:\n  {data_Client.base_url}')
    print(f' --> Client Backup:\n  {data_Client_bkp.base_url}')
    print(delimt)
    print('')
    print(" --------- Iniciando o ProcessarID.py --------- ")
    main(IDs, data_Client, data_Client_bkp)
