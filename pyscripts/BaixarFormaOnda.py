# -*- coding: utf-8 -*-
# Python 3.10
# ./Classificador_Sismologico/pyscripts/BaixarFormaOnda.py


# ----------------------------  DESCRIPTION  -----------------------------------
# Script para Baixar Forma de Onda (.mseed) dados sismicos
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.1
# Data: 2024-03-06


# Catalogo: MOHO-IAG-USP Brasileiro
#
# Client -> 'USP'
#
# EVENTOS -> ID de eventos ( 'Catalogo de Eventos' )
#
# Iterando sobre os eventos do catálogo:
#     - Se não houver PICKS, continue
#     - Obter a origem preferida (lat, long, profundidade)
#     Iterando sobre os picks do evento:
#         - Se pick.phase_hint != 'P', continue
#         - net = pick.waveform_id.network_code
#         - sta = pick.waveform_id.station_code
#         - sta_xy = get_sta_xy(net.sta)
#         - dist = get_distance(hypocenter, sta_xy)
#         - Se dist > 400, continue
#         - get_waveform(net, sta, pick.time, pick.time + 60)

# ----------------------------  IMPORTS   -------------------------------------
from obspy import UTCDateTime
from obspy.geodetics import gps2dist_azimuth

import os

from utils import get_sta_xy, delimt

# ---------------------------- PARAMETROS -------------------------------------
# Nome da pasta mseed
mseed_folder = "./mseed"
# Cria pasta se ela não existir
os.makedirs(mseed_folder, exist_ok=True)
# ---------------------------- FUNÇÕES ----------------------------------------


# Função para criar pasta para cada evento dentro de mseed
def create_event_dirname(origin_time):
    return origin_time.strftime("%Y%m%dT%H%M%S")


def save_waveforms(stream, network, station, origin_time):
    if not stream:
        print(f"Nenhum dado baixado para a estação {station}.")
        return
    event_dir = os.path.join(mseed_folder, create_event_dirname(origin_time))
    mseed_filename = os.path.join(event_dir,
                                  f"{network}_{station}_{create_event_dirname(origin_time)}.mseed")
    os.makedirs(event_dir, exist_ok=True)
    stream.write(mseed_filename, format="MSEED")


def download_waveforms(client, network, stations,
                       channel, start_time, end_time, origin_time):
    for station in stations:
        try:
            st = client.get_waveforms(network, station, "*",
                                      channel, start_time, end_time)
            save_waveforms(st, network, station, origin_time)
            print(f"Forma de onda baixada para a estação {station}.")
        except Exception as e:
            print(f"Erro ao baixar canal {channel} da estação {station}: {e}")


def download_and_save_waveforms(client, df, network_id, station_list,
                                channel_pattern):
    for index, row in df.iterrows():
        if index < 2:
            continue
        origin_time = UTCDateTime(row['Hora de Origem (UTC)'])
        start_time, end_time = origin_time - 10, origin_time + 50
        download_waveforms(client, network_id, station_list,
                           channel_pattern, start_time, end_time, origin_time)


def baixar_waveform(eventos, client, inventario):
    '''
    Baixa a forma de onda (.mseed) de um evento sísmico se a estação estiver a menos de 400 km do epicentro.
    '''
    for evento in eventos:
        print(f"Evento: {evento.resource_id.id}")
        if not evento.picks:
            print('Sem picks')
            continue

        origem = evento.preferred_origin()
        origem_lat = origem.latitude
        origem_lon = origem.longitude

        for pick in evento.picks:
            if pick.phase_hint != 'P':
                continue

            net = pick.waveform_id.network_code
            sta = pick.waveform_id.station_code
            print(f'net: {net}, sta: {sta}')

            sta_lat, sta_lon = get_sta_xy(net, sta, inventario)  # Assume que get_sta_xy retorna (latitude, longitude)
            if sta_lat is None or sta_lon is None:
                print(f"Estação {sta} da rede {net} não encontrada no inventário.")
                continue
            print(f'sta_xy: ({sta_lat}, {sta_lon})')

            dist, az, baz = gps2dist_azimuth(origem_lat, origem_lon, sta_lat, sta_lon)
            dist_km = dist / 1000  # Converte de metros para quilômetros
            print(f'Distância até o epicentro: {dist_km} km')

            if dist_km > 400:
                print("Estação a mais de 400 km do epicentro, forma de onda não será baixada.")
                continue

            # Prepara o intervalo de tempo para baixar a forma de onda baseado no tempo do pick
            start_time = pick.time - 10  # 10 segundos antes do pick
            end_time = pick.time + 50   # 50 segundos depois do pick

            # Baixa a forma de onda para a estação e intervalo de tempo específicos
            print('Baixando forma de onda...')
            download_waveforms(client, net, [sta], '*', start_time, end_time, pick.time)
            print(delimt)

    return None
