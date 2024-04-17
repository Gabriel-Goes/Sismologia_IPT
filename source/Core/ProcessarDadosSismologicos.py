# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/pyscripts/ProcessarDadosSismologicos.py

# ----------------------------  DESCRIPTION  -----------------------------------
# Script para gerar catálogo de eventos sísmicos
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.2
# Data: 2024-02-27
# Modificação mais recente: 2024-04-10

# ----------------------------  IMPORTS   -------------------------------------
from obspy.clients import fdsn
from obspy.core.event.catalog import Catalog

import sys
import os
from tqdm import tqdm
from typing import List, Dict

# ClassificadorSismologico
from BaixarFormaOnda import iterate_events
from utils import csv2list, delimt, inventory


# ---------------------------- FUNÇÕES ----------------------------------------
# FUNÇÃO MAIN QUE CONTERÁ AS CHAMADAS DAS FUNÇÕES
def main(IDs: List,
         data_Client: str,
         data_Client_bkp: str) -> [Catalog, Dict, List]:
    '''
    Função para processar os eventos sísmicos a partir de um catálogo de
    eventos previamente adquirido e disponibilizado no formato de um arquivo csv.
    '''
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

    # BAIXA A FORMA DE ONDA
    iterate_events(
        catalogo.events,
        data_Client,
        data_Client_bkp,
        inventory,
        baixar=True)  # FUNÇÃO PRINCIPAL DO SCRIPT

    # SAVE MISSING_IDS LIST TO CSV FILE
    os.makedirs('files/logs/missing_ids/bkp', exist_ok=True)
    # WRITE A CSV FILE WITH THE MISSING IDS
    with open('files/logs/missing_ids/missing_ids.csv', 'w') as f:
        f.write('ID\n')
        for id in missing_ids:
            f.write(f'{id}\n')

    return catalogo, inventory, missing_ids


# ---------------------------- MAIN -------------------------------------------
if __name__ == "__main__":
    print('')
    print(f' - Argumento 1: {sys.argv[1]}')

    moho_catalog_csv = sys.argv[1]
    IDs = csv2list(moho_catalog_csv, data=None)  # ADICIONE O ANO MAIS ANTIGO
    try:
        data_Client = fdsn.Client('http://seisarc.sismo.iag.usp.br/')
    except Exception as e:
        print(f'\nErro ao conectar com o servidor Seisarc.sismo.iag.usp.br: {e}')
        sys.exit(1)
    data_Client_bkp = fdsn.Client('http://rsbr.on.br:8081/fdsnws/dataselect/1/')

    print(f' --> Client:\n  {data_Client.base_url}')
    print(f' --> Client Backup:\n  {data_Client_bkp.base_url}')
    print(delimt)
    print('')

    print(" --------- Iniciando o ProcessarID.py --------- ")
    catalogo, inentory, missin_ids = main(
        IDs[:100],
        data_Client,
        data_Client_bkp)
