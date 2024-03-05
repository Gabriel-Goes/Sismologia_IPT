# -*- coding: utf-8 -*-
# Python 3.10
# ./Classificador_Sismologico/pyscripts/utils.py


# ----------------------------  DESCRIPTION  -----------------------------------
# Script para processar dados sismicos
# Autor: Gabriel Góes Rocha de Lima
# Funções de utilidade para Processar_Dados_Sismicos.py
# Versão: 0.1
# Data: 2024-02-27


# ----------------------------  IMPORTS   -------------------------------------
from obspy import UTCDateTime
from obspy.clients import fdsn
import os

from Exporter import Exporter


# ---------------------------- PARAMETROS -------------------------------------
# Nome da pasta mseed
folder_name = "./mseed"
# Cria pasta se ela não existir
os.makedirs(folder_name, exist_ok=True)


# ---------------------------- FUNÇÕES ----------------------------------------
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


# Função para criar pasta para cada evento dentro de mseed
def create_event_dirname(origin_time):
    return origin_time.strftime("%Y%m%dT%H%M%S")


# FUNÇÃO PARA ADQUIRIR EVENTOS DO CLIENT
def get_catalog(client, start_time, end_time):
    try:
        print(f"Time interval from {start_time} to {end_time}.")
        return client.get_events(starttime=start_time,
                                 endtime=end_time,
                                 includearrivals=True)
    except fdsn.header.FDSNNoDataException:
        print(' ------------------------------ Sem dados ------------------------------ ')
        print(f"No data for the period {start_time} to {end_time}.")
        return None


def save_waveforms(stream, network, station, origin_time):
    if not stream:
        print(f"Nenhum dado baixado para a estação {station}.")
        return

    event_dir = os.path.join(folder_name, create_event_dirname(origin_time))
    mseed_filename = os.path.join(event_dir, f"{network}_{station}_{create_event_dirname(origin_time)}.mseed")
    os.makedirs(event_dir, exist_ok=True)
    stream.write(mseed_filename, format="MSEED")


def download_waveforms(client, network, stations,
                       channel, start_time, end_time, origin_time):
    for station in stations:
        try:
            st = client.get_waveforms(network, station, "*",
                                      channel, start_time, end_time)
            save_waveforms(st, network, station, origin_time)
        except Exception as e:
            print(f"Erro ao baixar canal {channel} da estação {station}: {e}")


def download_and_save_waveforms(client, df, network_id, station_list,
                                channel_pattern):
    for index, row in df.iterrows():
        if index < 2:
            continue
        # print(row)
        origin_time = UTCDateTime(row['Hora de Origem (UTC)'])
        start_time, end_time = origin_time - 10, origin_time + 50
        download_waveforms(client, network_id, station_list,
                           channel_pattern, start_time, end_time, origin_time)
