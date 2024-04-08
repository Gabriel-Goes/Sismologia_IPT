# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/pyscripts/ProcessarID.py

# ----------------------------  DESCRIPTION  -----------------------------------
# Script para gerar catálogo de eventos sísmicos
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.1
# Data: 2024-02-27

# ----------------------------  IMPORTS   -------------------------------------
from obspy.clients import fdsn
from obspy.core.event.catalog import Catalog

import sys
import os
from tqdm import tqdm
from typing import List, Str

# ClassificadorSismologico
from BaixarFormaOnda import iterate_events
from utils import csv2list, bkp_time, cria_sta_dic, list_inventario, delimt, get_inventory_from_xml


# ---------------------------- FUNÇÕES ----------------------------------------
# função main que conterá as chamadas das funções
def main(IDs: List,
         data_Client: Str,
         data_Client_bkp: Str) -> [Catalog, List]:
    '''
    Função para processar os eventos sísmicos a partir de um catálogo de
    eventos previamente adquirido e disponibilizado no formato de um arquivo csv.
    '''
    # CONSTROI O INVENTARIO DE ESTAÇÕES
    inventario = {}
    print(' --> Inventário de Estações:')
    for file in list_inventario:
        # CHECK IF THE FILE IS A .TXT
        if file.endswith('.txt'):
            txt = file
            print(f' - Arquivo: {txt}')
            inventario = cria_sta_dic('./files/inventario/' + txt, inventario)
        # print(f' - {len(inventario)}')
    inventory = get_inventory_from_xml(
        'files/inventario/inventario_rsbr.xml',
        inventario)
    print(delimt)

    # GERAR O CATÁLOGO DE EVENTOS
    print(' ------------------------------ Acessando Catálogo ------------------------------ ')
    catalogo = Catalog()
    missing_ids = []
    for id in tqdm(IDs):
        try:
            temp_cat = data_Client.get_events(eventid=id, includearrivals=True)
            catalogo.append(temp_cat.events[0])

        except Exception:
            try:
                print(' Catalogo USP não encontrado. Tentando no servidor da RSBR.')
                temp_cat = data_Client_bkp.get_events(eventid=id, includearrivals=True)
                catalogo.append(temp_cat.events[0])

            except Exception:
                print(' ------------------------------ Sem dados ------------------------------ ')
                print(f"ID {id} não encontrado.")
                missing_ids.append(id)

    # Baixa a forma de onda
    iterate_events(
        catalogo.events,
        data_Client,
        data_Client_bkp,
        inventory,
        baixar=True)  # FUNÇÃO PRINCIPAL DO SCRIPT

    # Save missing_ids list to csv file
    os.mkdir('files/logs/erros/bkp', exist_ok=True)
    if os.path.exists('files/logs/erros/*_missing_ids.csv'):
        os.move('files/logs/erros/*_missing_ids.csv',
                'files/logs/erros/bkp/')

    with open('files/logs/erros/' + bkp_time + 'missing_ids.csv', 'w') as f:
        for item in missing_ids:
            f.write("%s\n" % item)

    return catalogo, inventory, missing_ids


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
    catalogo, inentory, missin_ids = main(
        IDs,
        data_Client,
        data_Client_bkp)
