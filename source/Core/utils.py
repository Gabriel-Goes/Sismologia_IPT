# -*- coding: utf-8 -*-
# Python 3.10
# ./Classificador_Sismologico/source/Core/utils.py


# ----------------------------  DESCRIPTION  ----------------------------------
# FUNÇÕES E VARIÁVEIS UTILITAŔIAS PARA O PROJETO
# Estas funções estão escritas aqui para melhorar a leitura dos scripts
# principais, aumentando a fluidez dos códigos deixando explícito apenas o que
# é realmente importante.

# Autor: Gabriel Góes Rocha de Lima
# Funções de utilidade para Processar_Dados_Sismicos.py
# Versão: 0.2.1
# Data: 2024-02-27
# Modificação 2024-04-10


# ----------------------------  IMPORTS   -------------------------------------
from datetime import datetime
import os
import sys
import pandas as pd
import xml.etree.ElementTree as ET

from obspy import UTCDateTime
from obspy.clients.fdsn import Client as fdsn
from dateutil.relativedelta import relativedelta

# FUNÇÃO ADAPATADA DE fdsnws.py ( CÓDIGO DE M. BIANCHI )
from Core import Exporter


# ---------------------------- PARAMETROS -------------------------------------
# Diretório do projeto
PROJETO_DIR = os.environ['HOME'] + "/projetos/ClassificadorSismologico"
# Nome da pasta mseed
MSEED_DIR = PROJETO_DIR + "/files/mseed"

# Dicionário de Netowrk ID
# MOHO IAG = https://www.moho.iag.usp.br/fdsnws/ -> 'USP'
ID_dict = {"MC": '8091',
           "IT": '8091',
           "SP": '8085',
           "PB": '8093',
           "BC": '8089',
           'USP': 'USP'}

# Delimitador para prints
delimt = "-----------------------------------------------------\n"
delimt2 = "#####################################################\n"

# Configura string de data para salvar arquivos
bkp_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# ---------------------------- FUNÇÕES ----------------------------------------
# FUNÇÃO PARA GERAR LOGS
class DualOutput(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self,
              message: str) -> None:
        self.terminal.write(message)
        self.log.write(message)

    def flush(self) -> None:  # NECESSÁRIO PARA A INTERFACE DE ARQUIVO
        self.terminal.flush()
        self.log.flush()


# FUNÇÃO PARA CRIAR UM DICIONÁRIO A PARTIR DE UM CSV
def csv2list(csv_file: str,
             data=False):
    '''
    Recebe um csv e retorna uma lista de EventID
    evid é a primeira coluna do header do csv
    evid = usp0000XXXX
    Se data for uma ano (ex: 2022), retorna uma lista com eventos a partir do
    ano até hoje;

    ex: data = 2010 -> retorna evid
    '''
    if data:
        with open(csv_file, 'r') as f:
            lines = f.readlines()
            evids = [line.split(',')[0] for line in lines[1:]]
        # SPLIT DEPOIS DO USP, E PEGA SÓ O ANO '0000' E SPLIT O XXXXX AS LETRAS
            evid = [int(evid.split('usp')[1][:4]) for evid in evids]
            if evid < data:
                return None
            else:
                return evid
    else:
        with open(csv_file, 'r') as f:
            lines = f.readlines()
            return [line.split(',')[0] for line in lines[1:]]


# Função para pegar o a (latitude, longitude) de uma estação
# e retornar um dicionário com as informações
def get_sta_xy(net, sta, cha, inventario):
    '''
        Recebe o network, station e channel e retorna a lat e long do sensor
    '''
    key = f"{net}.{sta}"
    try:
        # Filter the inventory for the given station and channel
        entries = inventory[(inventory['Network'] == net) & (inventory['Station'] == sta) & (inventory['Channel'] == cha)]
        if not entries.empty:
            # Check if all entries have the same latitude and longitude
            if entries['Latitude'].nunique() == 1 and entries['Longitude'].nunique() == 1:
                return entries.iloc[0]['Latitude'], entries.iloc[0]['Longitude']
            else:
                print(f"Error: Multiple coordinates for station {key} with channel {cha}.")
        else:
            print(f"No data for station {key} with channel {cha}.")
    except Exception as e:
        print(f"An error occurred while fetching coordinates for {key}: {str(e)}")
    return None, None

# para cada arquivo em um diretório, se for txt, lê e retorna um dataframe
def text2dataframe(directory):
    df_txt = pd.DataFrame()
    df_xml = pd.DataFrame()

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r') as f:
                # concatena os dataframes
                df_txt = pd.concat([df_txt, pd.read_csv(f, sep='\t')])
                print(df_txt.shape)
        elif filename.endswith(".xml"):
            with open(os.path.join(directory, filename), 'r') as f:
                # concatena os dataframes
                df_xml = pd.concat([df_xml, pd.read_csv(f, sep='\t')])
                print(df_xml.shape)
    return df_txt, df_xml


# FUNÇÃO PARA ADQUIRIR EVENTOS DO CLIENT
def get_catalog(client, start_time, end_time):
    try:
        return client.get_events(starttime=start_time,
                                 endtime=end_time,
                                 includearrivals=True)
    except fdsn.header.FDSNNoDataException:
        print(' ----------------------- Sem dados -------------------------- ')
        print(f"No data for the period {start_time} to {end_time}.")
        return None


# ---------------------------- FUNÇÕES OBSOLETE -------------------------------
# Função que retorna o catalogo de enventos sismicos de acordo com o periodo
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
        taa = UTCDateTime(start_time.datetime + relativedelta(months=1))\
            if mode == "m" else end_time
        print('')
        print(' -------------------- Acessando Catálogo -------------------- ')
        try:
            catalog = client.get_events(starttime=start_time,
                                        endtime=end_time,
                                        includearrivals=True)
        except fdsn.header.FDSNNoDataException:
            print(' -------------------- Sem dados ------------------------- ')
            print(f"No data for the period {start_time} to {end_time}.")
            return None

        # Termina o while com starttime = endtime
        start_time = taa
    return catalog


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


def parse_inventory_txt(file_path):
    df = pd.read_csv(file_path, sep='|', comment='#')
    df['key'] = df['Network'] + '.' + df['Station']
    return df


def parse_inventory_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    all_stations = []
    for network in root.findall('.//{http://www.fdsn.org/xml/station/1}Network'):
        network_code = network.get('code')
        for station in network.findall('.//{http://www.fdsn.org/xml/station/1}Station'):
            station_code = station.get('code')
            latitude = float(station.find('{http://www.fdsn.org/xml/station/1}Latitude').text)
            longitude = float(station.find('{http://www.fdsn.org/xml/station/1}Longitude').text)
            all_stations.append({'Network': network_code, 'Station': station_code, 'Latitude': latitude, 'Longitude': longitude, 'key': f"{network_code}.{station_code}"})
    return pd.DataFrame(all_stations)


def consolidate_inventory(inventory_files):
    inventory_df = pd.DataFrame()
    for file_path in inventory_files:
        if file_path.endswith('.txt'):
            inventory_df = pd.concat([inventory_df, parse_inventory_txt(PROJETO_DIR + f'/files/inventario/{file_path}')])
        elif file_path.endswith('.xml'):
            inventory_df = pd.concat([inventory_df, parse_inventory_xml(PROJETO_DIR + f'/files/inventario/{file_path}')])
    return inventory_df.set_index('key')


# Example usage:
inventory = consolidate_inventory(os.listdir(PROJETO_DIR + '/files/inventario'))
# print(inventory.head())
