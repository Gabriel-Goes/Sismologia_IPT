# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/pyscripts/ProcessarDadosSismologicos.py

# ----------------------------  DESCRIPTION  -----------------------------------
# Script para gerar catálogo de eventos sísmicos
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.2.0
# Data: 2024-02-27
# Modificação mais recente: 2024-04-10

# ----------------------------  IMPORTS   -------------------------------------
from obspy.core.event.catalog import Catalog
from obspy.geodetics import gps2dist_azimuth
from obspy.clients.fdsn import Client

import sys
import os
import csv
import random
import numpy as np
from tqdm import tqdm
from typing import List, Dict
import logging  # Utilizar o Logging

# ClassificadorSismologico
from nucleo.utils import MSEED_DIR
from nucleo.utils import DELIMT, DELIMT2
from nucleo.utils import csv2list


# Trocar prints por LOGGING
# ---------------------------- LOGGING ----------------------------------------
# logging.basicConfig(
#     filename='registros/fluxo_eventos.log',
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )


# ---------------------------- FUNÇÕES ----------------------------------------
def iterar_eventos(
        eventos: List,
        data_client: Client,
        data_client_bkp: Client,
        baixar=True,
        random=True
) -> None:
    print(' --> Iterando sobre eventos')
    print(f' - Número de eventos: {len(eventos)}')
    data_to_save = []
    error_to_save = []
    event_count = 0
    print(' --> Adquirindo Inventário de Estações')
    try:
        # IAG-USP
        inventario = data_client.get_stations(level='channel')
    except Exception as e:
        print(f'Erro ao adquirir inventário de estações: {e}')
        sys.exit(1)
    print(' Inventario adquirido com sucesso')
    print(f'{inventario.get_contents()["networks"][:5]} ... ')
    # print(inventario_bkp.get_contents()['networks'][:5])

    for evento in tqdm(eventos):
        event_id = evento.resource_id.id.split("/")[-1]
        event_count += 1
        print(f'############ Event {event_count}: {event_id} ############\n')
        if not evento.picks:
            error_to_save.append({'EventID': event_id,
                                  'Error': 'Sem picks'})
            print('Sem picks')
            print(DELIMT)
            continue

        origem = evento.preferred_origin()
        origem_lat = origem.latitude
        origem_lon = origem.longitude
        origem_depth = origem.depth
        origin_time = origem.time
        dir_name = origin_time.strftime("%Y%m%dT%H%M%S")
        pick_count = 0
        for pick in evento.picks:
            if pick.phase_hint not in ['P'] or pick.waveform_id.channel_code[:1] != 'H':
                error_to_save.append({'EventID': event_id,
                                      'Event': dir_name,
                                      'Network': pick.waveform_id.network_code,
                                      'Station': pick.waveform_id.station_code,
                                      'Location': pick.waveform_id.location_code,
                                      'Channel': pick.waveform_id.channel_code,
                                      'Origin Time': origin_time,
                                      'Origem Latitude': origem_lat,
                                      'Origem Longitude': origem_lon,
                                      'Depth/km': origem_depth,
                                      'Pick': pick.phase_hint,
                                      'Error': 'Pick diferente de P, Pg ou Pn ou Channel diferente de H'})
                continue

            pick_count += 1
            # print(f'--> Pick {pick_count}')
            net = pick.waveform_id.network_code
            sta = pick.waveform_id.station_code
            chn_ = pick.waveform_id.channel_code
            loc = pick.waveform_id.location_code

            chn = chn_[:-1] + 'Z'
            if loc is None:
                loc = ''
            seed_id = f'{net}.{sta}.{loc}.{chn}'
            try:
                cha_meta = inventario.get_channel_metadata(seed_id)
            except Exception as e:
                print(f' - Erro ao adquirir metadata de canais: {e}')
                error_to_save.append({
                    'EventID': event_id,
                    'Event': dir_name,
                    'Pick': pick.phase_hint,
                    'Network': net,
                    'Station': sta,
                    'Channel': chn,
                    'Location': loc,
                    'Origin Time': origin_time,
                    'Origem Latitude': origem_lat,
                    'Origem Longitude': origem_lon,
                    'Depth/km': origem_depth,
                    'Error': f'channel metadata: {e}'
                })
                print(f' - Fatal: nenhum metadado encontrado para canal {e}')
                continue

            sta_lat = cha_meta['latitude']
            sta_lon = cha_meta['longitude']
            if not sta_lat or not sta_lon:
                error_to_save.append({'EventID': event_id,
                                      'Event': dir_name,
                                      'Pick': pick.phase_hint,
                                      'Network': net,
                                      'Station': sta,
                                      'Pick Latitude': sta_lat,
                                      'Pick Longitude': sta_lon,
                                      'Origem Latitude': origem_lat,
                                      'Origem Longitude': origem_lon,
                                      'Depth/km': origem_depth,
                                      'Origin Time': origin_time,
                                      'Pick Time': pick.time,
                                      'Channel': chn,
                                      'Location': loc,
                                      'Error': 'sta_lat or sta_lon is None'
                                      })
                print(' - sta_lat or sta_lon is None')
                continue

            dist, az, baz = gps2dist_azimuth(
                origem_lat, origem_lon, sta_lat, sta_lon
            )
            dist_km = dist / 1000  # Converte de metros para quilômetros

            if dist_km > 400:
                error_to_save.append({'EventID': event_id,
                                      'Event': dir_name,
                                      'Pick': pick.phase_hint,
                                      'Network': net,
                                      'Station': sta,
                                      'Latitude': sta_lat,
                                      'Longitude': sta_lon,
                                      'Channel': chn,
                                      'Location': loc,
                                      'Distance': dist_km,
                                      'Depth/km': origem_depth,
                                      'Origem Latitude': origem_lat,
                                      'Origem Longitude': origem_lon,
                                      'Origin Time': origin_time,
                                      'Error': 'dist_km > 400 km'
                                      })
                continue

            if baixar:
                np.random.seed(42)
                random_offset = np.random.randint(5, 21)
                start_time = pick.time - random_offset
                end_time = start_time + 60
                try:
                    st = data_client.get_waveforms(
                        net, sta, loc, 'HH*',
                        start_time, end_time
                    )
                    print(f'--> Pick {pick_count}')
                    print(f' - Seed EventID: {seed_id} ')
                    print(f' - channel: {chn_}')
                    print(f' - {net}.{sta} X,Y : {sta_lat}, {sta_lon}')
                    print(f' - Distância até o epicentro: {dist_km} km')
                    # print(DELIMT)
                    print(' Downloading ...')
                    print(f' Pick Time -> {pick.time}')
                    print(f' Origin Time -> {origin_time}')
                    print(f' Channel -> {chn}')
                    print(
                        " - Waveform baixada para:\n",
                        f"- estação {sta}\n   - canal: {chn}")

                except Exception as e:
                    print(f"Canal {chn} da estação {sta}!\n   ERROR:  {e}")
                    try:
                        st = data_client_bkp.get_waveforms(
                            net, sta, loc, 'HH*',
                            start_time, end_time)
                        print(' Downloading ...')
                        print(f' Pick Time -> {pick.time}')
                        print(f' Origin Time -> {origin_time}')
                        print(f' Channel -> {chn}')
                        print(f" - Waveform baixada para a estação {sta}.")
                        print(DELIMT)

                    except Exception as e:
                        error_to_save.append({
                            'EventID': event_id,
                            'Event': dir_name,
                            'Pick': pick.phase_hint,
                            'Network': net,
                            'Station': sta,
                            'Latitude': sta_lat,
                            'Longitude': sta_lon,
                            'Channel': chn,
                            'Location': loc,
                            'Distance': dist_km,
                            'Pick Time': pick.time,
                            'Origin Time': origin_time,
                            'Origem Latitude': origem_lat,
                            'Origem Longitude': origem_lon,
                            'Depth/km': origem_depth,
                            'Start Time': start_time,
                            'End Time': end_time,
                            'Error': f'Download Error: {e}'
                        })
                        print(f" Falhou para todos os clientes: {e}")
                        continue
                if not st:
                    error_to_save.append({
                        'EventID': event_id,
                        'Event': dir_name,
                        'Pick': pick.phase_hint,
                        'Network': net,
                        'Station': sta,
                        'Latitude': sta_lat,
                        'Longitude': sta_lon,
                        'Channel': chn,
                        'Location': loc,
                        'Distance': dist_km,
                        'Pick Time': pick.time,
                        'Origin Time': origin_time,
                        'Origem Latitude': origem_lat,
                        'Origem Longitude': origem_lon,
                        'Depth/km': origem_depth,
                        'Start Time': start_time,
                        'End Time': end_time,
                        'Error': 'Stream is None'
                    })
                    print(" - Erro: Stream vazia")
                    continue

                event_name = origin_time.strftime("%Y%m%dT%H%M%S")
                print(f" - Diretório event_name: {event_name}")
                event_dir = os.path.join(MSEED_DIR, event_name)
                event_path = os.path.join(
                    event_dir, f"{net}_{sta}_{event_name}.mseed"
                )
                os.makedirs(event_dir, exist_ok=True)
                st.write(event_path, format="MSEED")

            try:
                magnitude = evento.preferred_magnitude().mag
            except Exception as e:
                print(f" -> Erro ao obter magnitude: {e}")
                error_to_save.append({
                    'Event': dir_name,
                    'Pick': pick.phase_hint,
                    'Network': net,
                    'Station': sta,
                    'Latitude': sta_lat,
                    'Longitude': sta_lon,
                    'Channel': chn,
                    'Location': loc,
                    'Distance': dist_km,
                    'Pick Time': pick.time,
                    'Origin Time': origin_time,
                    'Origem Latitude': origem_lat,
                    'Origem Longitude': origem_lon,
                    'Depth/km': origem_depth,
                    'Start Time': start_time,
                    'End Time': end_time,
                    'Error': f'No Magnitude: {e}'
                })
                magnitude = "None"

            data_to_save.append({
                'EventID': event_id,
                'Event': dir_name,
                'Origin Time': origin_time,
                'Origem Longitude': origem_lon,
                'Origem Latitude': origem_lat,
                'Depth/km': origem_depth,
                'Latitude': sta_lat,
                'Longitude': sta_lon,
                'MLv': magnitude,
                'Distance': dist_km,
                'Cat': evento.event_type,
                'Certainty': evento.event_type_certainty,
                'Pick': pick.phase_hint,
                'Network': net,
                'Station': sta,
                'Channel': chn,
                'Location': loc,
                'Pick Time': pick.time,
                'Start Time': start_time,
                'End Time': end_time,
                'Path': f"{event_name}/{net}_{sta}_{event_name}.mseed",
                'Error': None,
            })

            print(DELIMT)
        print(f' - Event: {event_id}')
        print(f' - Pwave Picks: {pick_count}')
        print(DELIMT2)

    csv_file_path = 'arquivos/eventos/eventos.csv'
    with open(
        csv_file_path, mode='w', newline='\n', encoding='utf-8'
    ) as csv_file:
        fieldnames = ['EventID', 'Event', 'Error',
                      'Pick', 'Network', 'Station', 'Location', 'Channel',
                      'Latitude', 'Longitude', 'Distance',
                      'Origem Latitude', 'Origem Longitude', 'Depth/km',
                      'Pick Time', 'Origin Time', 'Start Time', 'End Time',
                      'Cat',
                      'MLv', 'Certainty',
                      'Path']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_to_save:
            writer.writerow(data)

    print(f'Dados salvos com sucesso em {csv_file_path}')
    csv_error_path = 'arquivos/eventos/erros.csv'
    with open(
        csv_error_path, mode='w', newline='\n', encoding='utf-8'
    ) as csv_file:
        fieldnames = ['EventID', 'Event',
                      'Pick', 'Network', 'Station', 'Location', 'Channel',
                      'Latitude', 'Longitude', 'Distance',
                      'Origem Latitude', 'Origem Longitude', 'Depth/km',
                      'Pick Time', 'Origin Time', 'Start Time', 'End Time',
                      'Cat',
                      'MLv', 'Certainty',
                      'Path',
                      'Error']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data in error_to_save:
            writer.writerow(data)

    print(f'Erros salvos com sucesso em {csv_error_path}')

    return


# ---------------------------- MAIN -------------------------------------------
def fluxo_eventos(
        EventIDs: List,
        DATA_CLIENT: Client,
        DATA_CLIENT_BKP: Client) -> [Catalog, Dict, List]:

    print(" --------- INICIANDO FLUXO DE EVENTOS  --------- ")
    print('')
    print(' ------------------------------ ACESSANDO CATÁLOGO ------------------------------ ')
    print(f' - Catálogo: {sys.argv[1]}')
    print(f' - Primeiro EventID: {EventIDs[0]}')
    print(f' - EventID mediano: {EventIDs[int(len(EventIDs) / 2)]}')
    print(f' - Último EventID: {EventIDs[-1]}')
    catalogo = Catalog()
    ids_faltantes = []
    for id in tqdm(EventIDs):
        try:
            temp_cat = DATA_CLIENT.get_events(eventid=id, includearrivals=True)
            catalogo.append(temp_cat.events[0])

        except Exception:
            try:
                ids_faltantes.append(id + ' Não encontrado no servidor USP.')
                print(' Catalogo USP não encontrado. Tentando no servidor da RSBR.')
                temp_cat = DATA_CLIENT_BKP.get_events(
                    eventid=id,
                    includearrivals=True
                )
                catalogo.append(temp_cat.events[0])

            except Exception:
                print(' ------------------------------ Sem dados ------------------------------ ')
                print(f"EventID {id} não encontrado.")
                ids_faltantes.append(id + ' Não encontrado no servidor RSBR.')

    iterar_eventos(
        catalogo.events,
        DATA_CLIENT,
        DATA_CLIENT_BKP
    )

    os.makedirs('arquivos/registros/.bkp', exist_ok=True)
    with open('arquivos/registros/id_faltantes.csv', 'w') as f:
        f.write('EventID\n')
        for id in ids_faltantes:
            f.write(f'{id}\n')

    return catalogo, ids_faltantes


# ---------------------------- MAIN -------------------------------------------
def main(
    EventIDs: List,
):
    try:
        # DATA_CLIENT = Client('http://seisarc.sismo.iag.usp.br/')
        # DATA_CLIENT = Client('USP')
        DATA_CLIENT = Client("http://10.110.1.132:18003")
    except Exception as e:
        print(f'\nErro ao conectar com o servidor Seisarc.sismo.iag.usp.br: {e}')
        sys.exit(1)
    try:
        DATA_CLIENT_BKP = Client('http://rsbr.on.br:8081')
    except Exception as e:
        print(f'\nErro ao conectar com o servidor rsbr.on.br: {e}')
        sys.exit(1)

    catalogo, missin_ids = fluxo_eventos(
        EventIDs,
        DATA_CLIENT,
        DATA_CLIENT_BKP)

    return catalogo, missin_ids


if __name__ == "__main__":
    print('./fonte/nucleo/fluxo_eventos.py...')
    print(f' - Número de argumentos: {len(sys.argv)}')
    print(' - Argumentos (Roteiro Python | Catálogo de Eventos | Modo de Teste):')
    for n in range(len(sys.argv)):
        print(f' {sys.argv[n]}')
    EventIDs = csv2list(sys.argv[1])
    print(sys.argv[2])
    if sys.argv[2] == 'True':
        print(' --> Modo de teste ativado')
        random.seed(42)
        EventIDs = random.sample(EventIDs, 1500)
        print(f' - Número de EventIDs: {len(EventIDs)}')

    catalogo, missin_ids = main(EventIDs)
