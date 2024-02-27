# -*- coding: utf-8 -*-
# ----------------------------  DESCRIPTION  -----------------------------------
# Script para processar dados sismicos
# Autor: Gabriel Góes Rocha de Lima
# Alterado de fdsnwscsv.py (por Bianchi)
# Versão: 1.0
# Data: 2024-02-27
# ----------------------------  IMPORTS   -------------------------------------
import pandas as pd
from obspy import UTCDateTime
from obspy.clients import fdsn
import sys
import os
import utm
from dateutil.relativedelta import relativedelta
# from obspy import Stream
# ---------------------------- CONSTANTES -------------------------------------
# Nome da pasta mseed
folder_name = "mseed"
# Cria pasta se ela não existir
os.makedirs(folder_name, exist_ok=True)
# Função para criar pasta para cada evento dentro de mseed
def create_event_dirname(origin_time):
    return origin_time.strftime("%Y%m%dT%H%M%S")
# -----------------------------------------------------------------------------
# Classe Exporter
class Exporter(object):
    def __init__(self, sep=";", where=sys.stderr):
        self._ = False
        if isinstance(where, str):
            where = open(where, "w")
            self._iopen = True
        self._where = where
        self._gotheader = False
        self._sep = sep
        self.fformat = "{:8.4f}"

    def __enter__(self):
        if self._iopen:
            print("Writing to file: {}".format(self._where.name))
        return self

    def __exit__(self, type, value, tb):
        if self._iopen:
            print("Closing file {}.".format(self._where.name))
            self._where.close()

    def translate(self, evtype):
        evlist = {
            'earthquake': 'E',
            'quarry blast': 'Q',
            'induced or triggered event': 'I'
        }
        if evtype not in evlist:
            # Alterei None para esta string
            return 'Not defined in the list'
        return evlist[evtype]

    def flushheader(self):
        if self._gotheader:
            return
        headers = ['ID', 'Hora de Origem (UTC)', 'Longitude', 'Latitude',
                   'UTM X', 'UTM Y', 'MLv', 'Energia', 'Cat']
        headersu = ['', '', '(°)', '(°)', '(m)', '(m)', '', '(J)', '']
        print(self._sep.join(headers), file=self._where)
        print(self._sep.join(headersu), file=self._where)
        self._gotheader = True

    def feed(self, e, o, m, ID):
        if e.event_type not in ['earthquake', 'quarry blast',
                                'induced or triggered event']:
            print("Event type not supported: {}".format(e.event_type))
            return False

        self.flushheader()

        data = []
        if e.resource_id.id.split("/")[-1].split("_")[0] ==\
                ID or e.resource_id.id.split("/")[-1].split("z")[0] == 'gf':

            # Id
            data.append(e.resource_id.id.split("/")[-1])

            # Origin Time
            t = e.preferred_origin().time
            data.append(t.strftime("%Y-%m-%dT%H:%M:%S"))

            # Coords
            data.append(self.fformat.format(o.longitude))
            data.append(self.fformat.format(o.latitude))

            # UTM
            if o.latitude <= 84 and o.latitude >= -84:
                (ux, uy, _, _) = utm.from_latlon(o.latitude, o.longitude)
                data.append("{}".format(ux))
                data.append("{}".format(uy))
            else:
                data.extend([None, None])

            # Magnitude
            try:
                data.append("{:3.1f}".format(m.mag))
            except AttributeError:
                print("Event has no magnitude --- {}".format(e.resource_id.id))
                return False

            E = 10 ** (9.9 + 1.9 * m.mag - 0.0024 * m.mag ** 2) / 1.0E7
            data.append("{:g}".format(E))

            data.append(self.translate(e.event_type))

            print(self._sep.join(map(str, data)), file=self._where)

            return True

# FUNÇÃO PARA ADQUIRIR EVENTOS DO CLIENT
def get_catalog(client, start_time, end_time):
    try:
        print(f"Time interval from {start_time} to {end_time}.")
        return client.get_events(starttime=start_time, endtime=end_time, includearrivals=True)

    except fdsn.header.FDSNNoDataException:
        print(' ------------------------------ Sem dados ------------------------------ ')
        print(f"No data for the period {start_time} to {end_time}.")
        return None


def write_event_data(event, exporter, network_id):
    origin = event.preferred_origin()
    magnitude = event.preferred_magnitude()
    return exporter.feed(event, origin, magnitude, network_id)


def process_catalog(catalog, filename, network_id):
    with Exporter(where=filename) as exporter:
        for event in catalog:
            if not write_event_data(event, exporter, network_id):
                print(f"Skipped event {event.resource_id.id}")


def download_and_save_waveforms(client, df, network_id, station_list,
                                channel_pattern):
    for index, row in df.iterrows():
        if index < 2:
            continue

        print(row)
        origin_time = UTCDateTime(row['Hora de Origem (UTC)'])
        start_time, end_time = origin_time - 10, origin_time + 50
        download_waveforms(client, network_id, station_list,
                           channel_pattern, start_time, end_time, origin_time)


def download_waveforms(client, network, stations,
                       channel, start_time, end_time, origin_time):
    for station in stations:
        try:
            st = client.get_waveforms(network, station, "*",
                                      channel, start_time, end_time)
            save_waveforms(st, network, station, origin_time)
        except Exception as e:
            print(f"Erro ao baixar canal {channel} da estação {station}: {e}")


def save_waveforms(stream, network, station, origin_time):
    if not stream:
        print(f"Nenhum dado baixado para a estação {station}.")
        return

    event_dir = os.path.join(folder_name, create_event_dirname(origin_time))
    mseed_filename = os.path.join(event_dir,f"{network}_{station}_{create_event_dirname(origin_time)}.mseed")

    os.makedirs(event_dir, exist_ok=True)
    stream.write(mseed_filename, format="MSEED")


def main(start_time, end_time, network_id, mode):
    client = fdsn.Client('http://localhost:' + ID_dict[network_id])
    print(f' --> Client:\n  {client}')
    print('')
    while start_time < end_time:
        print(f"Start time: {start_time}")
        taa = UTCDateTime(start_time.datetime + relativedelta(months=1)) if mode == "m" else end_time
        filename = start_time.strftime("events-%Y-%m-%d") + f"-{network_id}.csv" if mode == "m" else "events-all.csv"
        print(' ------------------------------ Acessando Catálogo ------------------------------ ')
        catalog = get_catalog(client, start_time, taa)

        if catalog:
            print(' ----------------------------- Processando Catálogo ---------------------------- ')
            process_catalog(catalog, filename, network_id)

        start_time = taa

    print(' ----------- Baixando waveforms -----------')
    df = pd.read_csv(f'./{filename}', sep=';')
    download_and_save_waveforms(client, df, network_id, ["IT9", "IT1"], "HH?")


if __name__ == "__main__":
    ta = UTCDateTime(sys.argv[1])
    te = UTCDateTime(sys.argv[2])
    ID = sys.argv[3]
    mode = "t"  # Supondo que o modo sempre será "t"
    ID_dict = {"MC": '8091',
               "IT": '8091',
               "SP": '8085',
               "PB": '8093',
               "BC": '8089'}

    print(" --------- Iniciando o fdsnwscsv_ggrl.py --------- ")
    main(ta, te, ID, mode)
