# -*- coding: utf-8 -*-
# Python 3.10
# ./Classificador_Sismologico/pyscripts/ProcessarCatalogoSismo.py


# ----------------------------  DESCRIPTION  -----------------------------------
# Script para gerar catálogo de sismos
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.1
# Data: 2024-03-05


# ----------------------------  IMPORTS   -------------------------------------
from obspy import UTCDateTime
from obspy.clients import fdsn
from dateutil.relativedelta import relativedelta
import sys
from utils import get_catalog


# ---------------------------- FUNÇÕES ----------------------------------------
def catalogo(start_time, end_time, network_id, mode):
    # Para conectar ao servidor MOHO IAG (USP)
    if network_id == 'USP':
        client = fdsn.Client('USP')
    else:
        client = fdsn.Client('http://localhost:' + ID_dict[network_id])
    print(f' --> Client:\n  {client}')
    print('')
    while start_time < end_time:
        print(f" -> Data de Início: {start_time.date}")
        print(f" -> Data de Fim:    {end_time.date}")
        taa = UTCDateTime(start_time.datetime + relativedelta(months=1)) if mode == "m" else end_time
        print('')
        print(' ------------------------------ Acessando Catálogo ------------------------------ ')
        catalog = get_catalog(client, start_time, taa)
        if catalog:
            print('')
            print(' ----------------------------- Processando Catálogo ---------------------------- ')
        # Termina o while com starttime = endtime
        start_time = taa


# ---------------------------- MAIN -------------------------------------------
if __name__ == "__main__":
    print('')
    print(f' - Argumento 1: {sys.argv[1]}')
    print(f' - Argumento 2: {sys.argv[2]}')
    print(f' - Argumento 3: {sys.argv[3]}')
    ta = UTCDateTime(sys.argv[1])
    te = UTCDateTime(sys.argv[2])
    ID = sys.argv[3]
    mode = "t"  # Supondo que o modo sempre será "t"
    # MOHO IAG = https://www.moho.iag.usp.br/fdsnws/
    ID_dict = {"MC": '8091',
               "IT": '8091',
               "SP": '8085',
               "PB": '8093',
               "BC": '8089',
               'USP': 'USP'}
    print('')
    print(" --------- Iniciando o fdsnwscsv.py --------- ")
    main(ta, te, ID, mode)
