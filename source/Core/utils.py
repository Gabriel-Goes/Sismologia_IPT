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
import xml.etree.ElementTree as ET
import sys

from obspy import UTCDateTime
from obspy.clients.fdsn import Client as fdsn
from dateutil.relativedelta import relativedelta
from obspy import read_inventory

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

# Caminho para diretório de invetário de redes sismológicas
path_inventario = PROJETO_DIR + '/files/inventario/'
list_inventarios = os.listdir(path_inventario)


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


# Função para ler um .txt e extrair o Netorw, Station e Latitute, Longitude
# e Depth e salvar  em um dicionário.
def cria_sta_dic(file: str,
                 dic):
    '''
    Recebe:
        file: caminho do arquivo .txt com informações da rede sismológica
         dic: Dicionário possivelmente vazio ou com prévias informações de
             network, station, latitude, longitude e depth.

    Retorna:
        Dicionário com as informações de network, station, latitude,
        longitude e depth de cada estação.

    Exemplo de arquivo .txt:

    #Network|Station|Location|Channel|Latitude|Longitude|Elevation|Depth|\
    Azimuth|Dip|SensorDescription|Scale|ScaleFreq|ScaleUnits|SampleRate|\
    StartTime|EndTime

    BR|AGBLB||BHE|-9.03868|-37.045358|448.0|0.0|90.0|0.0|STS-2, 120 s,\
    1500 V/m/s, generation 1 electronics|936717000.0|0.05|M/S|40.0|\
    2010-05-10T00:38:13.615|2012-09-14T00:44:13.24

    '''
    if not dic:
        dic = {}

    # print(f' - Arquivo: {file}')

    with open(file, 'r') as f:
        header = f.readline().strip().split('|')
        header = [h.replace('#', '') for h in header]
        idx_network = header.index('Network')
        idx_station = header.index('Station')
        idx_location = header.index('Location')
        idx_latitude = header.index('Latitude')
        idx_longitude = header.index('Longitude')
        idx_depth = header.index('Depth')

        for line in f:
            line = line.strip().split('|')
            network = line[idx_network]
            station = line[idx_station]
            location = line[idx_location]
            latitude = float(line[idx_latitude])
            longitude = float(line[idx_longitude])
            depth = float(line[idx_depth])

            key = f"{network}.{station}"
            if key not in dic:
                dic[key] = []

            dic[key].append({
                'network': network,
                'station': station,
                'location': location,
                'latitude': latitude,
                'longitude': longitude,
                'depth': depth
            })

    return dic


def get_inventory_from_xml(file: str,
                           dic):
    '''
    Lê um arquivo XML e extrai informações da rede sismológica para atualizar
    ou criar um dicionário.

    Parâmetros:
        file: caminho para o arquivo XML com as informações da rede
              sismológica.
        dic: dicionário possivelmente vazio ou com informações prévias de
             network, station, latitude, longitude e depth.

    Retorna:
        Dicionário atualizado com as informações de network, station, latitude,
        longitude e depth de cada estação.
    '''
    if dic is None:
        dic = {}

    # Carrega o conteúdo do XML
    tree = ET.parse(file)
    root = tree.getroot()
    # Namespace para buscar as tags corretamente
    ns = {'ns': 'http://www.fdsn.org/xml/station/1'}

    # Itera sobre cada estação no XML
    for network in root.findall('ns:Network', ns):
        network_code = network.get('code')
        for station in network.findall('ns:Station', ns):
            station_code = station.get('code')
            latitude = station.find('ns:Latitude', ns).text
            longitude = station.find('ns:Longitude', ns).text
            #  elevation = station.find('ns:Elevation', ns).text
            # Gera a chave única para cada estação
            key = f"{network_code}.{station_code}"
            # Verifica se a estação já existe no dicionário
            if key not in dic:
                dic[key] = []
            # Adiciona ou atualiza a entrada da estação no dicionário
            dic[key].append({
                'network': network_code,
                'station': station_code,
                'latitude': float(latitude),
                'longitude': float(longitude),
                # 'depth': float(elevation)
            })
    return dic


# Função para pegar o a ('net.sta','lat','lon','depth')
# e retornar um dicionário com as informações
def get_sta_xy(net, sta, inventario):
    key = f"{net}.{sta}"
    if key in inventario:
        # Retorna a latitude e longitude encontradas no dicionário
        return inventario[key][0]['latitude'], inventario[key][0]['longitude']
    else:
        # Retorna None para ambos se a estação não for encontrada
        print(f"Estação {sta} da rede {net} não encontrada no inventário.")
        print(delimt)
        return None, None


def constroi_inventario():
    # CONSTROI O INVENTARIO DE ESTAÇÕES
    inventario = {}
    print(' --> Inventário de Estações:')
    for file in list_inventarios:
        # CHECK IF THE FILE IS A .TXT
        if file.endswith('.txt'):
            txt = file
            print(f' - Arquivo: {txt}')
            inventario = cria_sta_dic('./files/inventario/' + txt, inventario)
        print(f' - {len(inventario)}')
    inventory = get_inventory_from_xml(
        'files/inventario/inventario_rsbr.xml',
        inventario)
    print(delimt)

    return inventory, inventario


inventory = constroi_inventario()


# FUNÇÃO PARA GERAR INVENTÁRIO DE ESTAÇÕES SISMOLÓGICAS
def gera_inventario_txt(inv):
    inv = read_inventory("files/inventario.xml")
    inventario_txt = open("files/inventario.txt", "w")
    inventario_txt.write("Station,Latitude,Longitude\n")
    # cria um arquivo de texto com station code, latitude e longitude
    for network in inv:
        for station in network:
            lat = station.latitude
            lon = station.longitude
            inventario_txt.write(f"{station.code},{lat},{lon}\n")


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
        print(' ----------------------- Sem dados -------------------------- ')
        print(f"No data for the period {start_time} to {end_time}.")
        return None


# --------------------------------------------------------------------------- #
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
