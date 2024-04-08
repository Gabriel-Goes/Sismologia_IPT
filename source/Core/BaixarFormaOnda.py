# -*- coding: utf-8 -*-
# Python 3.10
# ./Classificador_Sismologico/pyscripts/BaixarFormaOnda.py


# ----------------------------  DESCRIPTION  -----------------------------------
# Script para Baixar Forma de Onda (.mseed) dados sismicos
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.1
# Data: 2024-03-06


# ----------------------------  IMPORTS   -------------------------------------
from obspy.geodetics import gps2dist_azimuth
import numpy as np
import csv
import os
from tqdm import tqdm

# NOSSAS FUNÇÕES
from utils import get_sta_xy, mseed_folder, delimt, delimt2


# --------------------------------- FUNÇÕES ---------------------------------- #
# Fixa a semente para garantir a reprodução
def download_and_save_waveforms_random(data_client, data_client_bkp,
                                       net, sta, loc, chn,
                                       pick_time, origin_time):
    np.random.seed(42)
    random_offset = np.random.randint(5, 21)
    start_time = pick_time - random_offset
    end_time = start_time + 60  # Mantém a janela de 60 segundos

    try:
        st = data_client.get_waveforms(
            net, sta, loc, chn,
            start_time, end_time)
        print(f" - Forma de onda baixada para:\n   - estação {sta}\n   - canal: {chn}")

    # If data_client fails, try data_client_bkp
    except Exception as e:
        print(f" ! Erro ao baixar canal {chn} da estação {sta}!\n   ERROR:  {e}")
        try:
            st = data_client_bkp.get_waveforms(
                net, sta, loc, chn,
                start_time, end_time)
            print(f" try 2 - Forma de onda baixada para a estação {sta}.")
            print(delimt)

        except Exception as e:
            print(f" ! Erro ao baixar canal {chn} da estação {sta}: {e}")

    except Exception as e:
        print(f" Falhou para todos os clientes: {e}")

    # Cria pasta se ela não existir
    os.makedirs(mseed_folder, exist_ok=True)

    event_name = origin_time.strftime("%Y%m%dT%H%M%S")
    print(f" - Nomeando diretório com origin_time: {event_name}")
    if not st:
        print(f"Nenhum dado baixado para a estação {sta}.")
        return

    event_dir = os.path.join(mseed_folder, origin_time.strftime("%Y%m%dT%H%M%S"))
    event_path = os.path.join(event_dir,
                              f"{net}_{sta}_{event_name}.mseed")
    os.makedirs(event_dir, exist_ok=True)
    st.write(event_path, format="MSEED")

    return st


def iterate_events(eventos, data_client, data_client_bkp, inventario, baixar=False):
    '''
    Baixa a forma de onda (.mseed) de um evento sísmico se a estação estiver a menos de 400 km do epicentro.
    '''
    # Agora, tanto print() quanto print(f'') serão exibidos no terminal e escritos em output.txt
    print(' --> Iterando sobre eventos')
    print(f' - Número de eventos: {len(eventos)}')
    print(f' - Client: {data_client.base_url}')
    print(f' - Client Backup: {data_client_bkp.base_url}')
    print(f' - Itens no Inventário: {len(inventario)}')
    input("Press Enter to continue ...\n")
    data_to_save = []  # Lista para coletar os dados que serão salvos no CSV
    event_count = 0
    for evento in tqdm(eventos):
        event_id = evento.resource_id.id.split("/")[-1]
        event_count += 1
        print(f'############ Event {event_count}: {event_id} ############\n')
        # Get number of picks in event
        if not evento.picks:
            print('Sem picks')
            print(delimt)
            continue

        origem = evento.preferred_origin()
        origem_lat = origem.latitude
        origem_lon = origem.longitude
        origin_time = origem.time
        dir_name = origin_time.strftime("%Y%m%dT%H%M%S")
        pick_count = 0
        stream_count = 0
        for pick in evento.picks:
            # Se pick.phase_hint for diferente de P ou Pg, continue
            if pick.phase_hint not in ['P', 'Pg', 'Pn']:
                # print(f" - Pick {pick.phase_hint} != 'P', continue")
                # print(delimt)
                continue

            pick_count += 1
            print(f'--> Pick {pick_count}')
            net = pick.waveform_id.network_code
            sta = pick.waveform_id.station_code
            cha = pick.waveform_id.channel_code
            loc = pick.waveform_id.location_code
            print(f' - Net: {net}\n - Sta: {sta}')

            sta_lat, sta_lon = get_sta_xy(net, sta, inventario)  # Assume que get_sta_xy retorna (latitude, longitude)
            if sta_lat is None or sta_lon is None:
                continue

            print(f' - X,Y {net}.{sta}: {sta_lat}, {sta_lon}')

            dist, az, baz = gps2dist_azimuth(origem_lat, origem_lon, sta_lat, sta_lon)
            dist_km = dist / 1000  # Converte de metros para quilômetros
            print(f' - Distância até o epicentro: {dist_km} km')

            if dist_km > 400:
                print("Estação a mais de 400 km do epicentro, forma de onda não será baixada.")
                print(delimt)
                continue

            if baixar:
                # Baixa a forma de onda para a estação e intervalo de tempo específicos
                np.random.seed(42)  # Fixa a semente para garantir a reprodução
                random_time = np.random.randint(5, 21)  # Deslocamento aleatório entre 5 e 20 segundos
                pick_time = pick.time
                start_time = pick_time - random_time
                end_time = start_time + 60  # Mantém a janela de 60 segundos

                print(' Downloading ...')
                print(f' Pick Time -> {pick.time}')
                print(f' Origin Time -> {origin_time}')
                print(f' Channel -> {cha}')

                try:
                    # st = download_waveforms(data_client, data_client_bkp, net, [sta], loc, cha, start_time, end_time, origin_time)
                    st = data_client.get_waveforms(net, sta, loc, 'HH*', start_time, end_time)
                    os.makedirs(f'./files/mseed/{dir_name}', exist_ok=True)
                    st.write(f'./files/mseed/{dir_name}/{net}_{sta}_{dir_name}.mseed', format="MSEED")
                    stream_count += 1
                    print(f' - Saving File: {dir_name}/{net}_{sta}_{dir_name}.mseed')

                except Exception as e:
                    print(f"Error downloading waveform: {e}")

                try:
                    magnitude = evento.preferred_magnitude().mag
                except Exception as e:
                    print(f" -> Erro ao obter magnitude: {e}")
                    magnitude = "None"

                # Aqui, você deve ajustar de acordo com os dados exatos que você quer salvar.
                # Isso é apenas um exemplo baseado no que você forneceu.
                data_to_save.append({
                    'ID': event_id,  # Substitua pela identificação correta do evento
                    'Hora de Origem (UTC)': origin_time,
                    'Longitude': origem_lon,
                    'Latitude': origem_lat,
                    'MLv': magnitude,  # Substitua pela magnitude do evento, se disponível
                    'Distance': dist_km,
                    'Folder': dir_name,
                    'Cat': evento.event_type,  # Substitua pela categoria do evento, se aplicável
                    'Certainty': evento.event_type_certainty  # Substitua pela certeza do evento, se aplicável
                })

                print(delimt)
        # Print number of Pwave Picks
        print(f' - Event: {event_id}')
        print(f' - Pwave Picks: {pick_count}')
        print(f' - Streams: {stream_count}')
        print(delimt2)

    # Escrever os dados coletados no arquivo CSV
    csv_file_path = './files/events-moho-catalog.csv'  # Substitua pelo caminho correto
    with open(csv_file_path, mode='w', newline='\n', encoding='utf-8') as csv_file:
        fieldnames = ['ID', 'Hora de Origem (UTC)', 'Longitude', 'Latitude', 'MLv', 'Distance', 'Folder', 'Cat', 'Certainty']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_to_save:
            writer.writerow(data)

    print(f'Dados salvos com sucesso em {csv_file_path}')

    return None
