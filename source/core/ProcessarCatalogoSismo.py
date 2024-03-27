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
from obspy.core.event.catalog import Catalog
from dateutil.relativedelta import relativedelta

from utils import ID_dict

# Classe adaptada do Bianchi (fdsnwscsv.py)
from Exporter import Exporter
from tqdm import tqdm


# ---------------------------- FUNÇÕES ----------------------------------------
# Função que retorna o catalogo de enventos sismicos
def gera_catalogo_datetime(start_time, end_time, network_id, mode):
    if network_id == 'USP':
        # Servidor MOHO IAG (USP)
        client = fdsn.Client('USP')
    else:
        # Servidor IPT
        client = fdsn.Client('http://localhost:' + ID_dict[network_id])
    print(f' --> Client:\n  {client}')
    print('')
    start_time = UTCDateTime(start_time)
    end_time = UTCDateTime(end_time)
    while start_time < end_time:
        print(f" -> Data de Início: {start_time.date}")
        print(f" -> Data de Fim:    {end_time.date}")
        taa = UTCDateTime(start_time.datetime + relativedelta(months=1)) if mode == "m" else end_time
        print('')
        print(' ------------------------------ Acessando Catálogo ------------------------------ ')
        try:
            catalog = client.get_events(starttime=start_time,
                                        endtime=end_time,
                                        includearrivals=True)
        except fdsn.header.FDSNNoDataException:
            print(' ------------------------------ Sem dados ------------------------------ ')
            print(f"No data for the period {start_time} to {end_time}.")
            return None

        # Termina o while com starttime = endtime
        start_time = taa
    return catalog


# Gera catalogo por event id
def gera_catalogo_event_id(IDs, data_Client, data_Client_bkp):
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

    return catalogo, missing_ids


# --------------------------------------------------------------------------- #
# Função que chama o exporter.feed(event, origin, magnitude, network_id)
def write_event_data(event, exporter, network_id):
    origin = event.preferred_origin()
    magnitude = event.preferred_magnitude()
    return exporter.feed(event, origin, magnitude, network_id)


def write_catalog(catalog, filename, network_id):
    with Exporter(where=filename) as exporter:
        print(f" --> Catalogo com {len(catalog)} eventos.")
        for event in catalog:
            if not write_event_data(event, exporter, network_id):
                print(f"Skipped event {event.resource_id.id}")


# FUNÇÃO PARA ADQUIRIR EVENTOS DO CLIENT
def get_catalog(client, start_time, end_time):
    try:
        return client.get_events(starttime=start_time,
                                 endtime=end_time,
                                 includearrivals=True)
    except fdsn.header.FDSNNoDataException:
        print(' ------------------------------ Sem dados ------------------------------ ')
        print(f"No data for the period {start_time} to {end_time}.")
        return None
