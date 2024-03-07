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
from obspy.geodetics import gps2dist_azimuth
import numpy as np

import os

from utils import get_sta_xy, delimt, mseed_folder

from tqdm import tqdm

# Cria pasta se ela não existir
os.makedirs(mseed_folder, exist_ok=True)
# ---------------------------- FUNÇÕES ----------------------------------------


# Função para criar pasta para cada evento dentro de mseed
def create_event_dirname(origin_time):
    dir_name = origin_time.strftime("%Y%m%dT%H%M%S")
    print(f" - Criando pasta para o evento: {dir_name}")
    return dir_name


def save_waveforms(stream, network, station, origin_time):
    if not stream:
        print(f"Nenhum dado baixado para a estação {station}.")
        return
    event_name = create_event_dirname(origin_time)
    event_dir = os.path.join(mseed_folder, event_name)
    mseed_filename = os.path.join(event_dir,
                                  f"{network}_{station}_{event_name}.mseed")
    os.makedirs(event_dir, exist_ok=True)
    stream.write(mseed_filename, format="MSEED")


def download_waveforms(data_client, data_client_bkp, network, stations,
                       channel, start_time, end_time, origin_time):
    for station in stations:
        try:
            st = data_client.get_waveforms(network, station, "*",
                                           channel, start_time, end_time)
            save_waveforms(st, network, station, origin_time)
            print(f" - Forma de onda baixada para a estação {station}.")
        # If data_client fails, try data_client_bkp
        except Exception as e:
            print(f" ! Erro ao baixar canal {channel} da estação {station}: {e}")
            try:
                st = data_client_bkp.get_waveforms(network, station, "*",
                                                   channel, start_time, end_time)
                save_waveforms(st, network, station, origin_time)
                print(f" try 2 - Forma de onda baixada para a estação {station}.")

            except Exception as e:
                print(f" ! Erro ao baixar canal {channel} da estação {station}: {e}")
        except Exception as e:
            print(f" Falhou para todos os clientes: {e}")


# Fixa a semente para garantir a reprodução
def download_and_save_waveforms_random(origin_time, data_client, data_client_bkp,
                                       network_id, station_list, channel_pattern):
    np.random.seed(42)
    # Extrai o tempo de origem do evento
    # Gera um deslocamento aleatório entre 5 a 20 segundos
    random_offset = np.random.randint(5, 21)
    # Calcula os novos tempos de início e fim baseado no deslocamento aleatório
    start_time = origin_time - random_offset
    end_time = start_time + 60  # Mantém a janela de 60 segundos
    # Chama a função para baixar as formas de onda
    download_waveforms(data_client, data_client_bkp, network_id, station_list,
                       channel_pattern, start_time, end_time, origin_time)
    # Substitua 'client', 'df', 'network_id', 'station_list', e 'channel_pattern' pelos seus valores reais


def baixar_waveform(eventos, data_client, data_client_bkp, inventario):
    '''
    Baixa a forma de onda (.mseed) de um evento sísmico se a estação estiver a menos de 400 km do epicentro.
    '''
    print(' --> Baixando Forma de Onda')
    # print(f' - Número de eventos: {len(eventos)}')
    # print(f' - Client: {client}')
    # print(f' - Tamanho do Inventário: {len(inventario)}')
    count = 0
    for evento in tqdm(eventos):
        count += 1
        print(f' ---> Event {count}')
        # print(f" - Resource ID: {evento.resource_id.id}")
        if not evento.picks:
            print('Sem picks')
            continue

        origem = evento.preferred_origin()
        origem_lat = origem.latitude
        origem_lon = origem.longitude
        origin_time = origem.time

        for pick in evento.picks:
            if pick.phase_hint != 'P':
                continue

            net = pick.waveform_id.network_code
            sta = pick.waveform_id.station_code
            cha = pick.waveform_id.channel_code
            print(f' - Net: {net}\n - Sta: {sta}')

            sta_lat, sta_lon = get_sta_xy(net, sta, inventario)  # Assume que get_sta_xy retorna (latitude, longitude)
            if sta_lat is None or sta_lon is None:
                print(f"Estação {sta} da rede {net} não encontrada no inventário.")
                print(delimt)
                continue
            print(f'- (X,Y) {net}.{sta}: ({sta_lat}, {sta_lon})')

            dist, az, baz = gps2dist_azimuth(origem_lat, origem_lon, sta_lat, sta_lon)
            dist_km = dist / 1000  # Converte de metros para quilômetros
            print(f'Distância até o epicentro: {dist_km} km')

            if dist_km > 400:
                print("Estação a mais de 400 km do epicentro, forma de onda não será baixada.")
                continue

            # Baixa a forma de onda para a estação e intervalo de tempo específicos
            print(' baixando...')
            print(f' pick.time -> {pick.time}')
            print(f' origin_time -> {origin_time}')
            print(f' Channel -> {cha}')
            download_and_save_waveforms_random(pick.time, data_client, data_client_bkp, net, [sta], 'HH*')
            print(delimt)

    return None
