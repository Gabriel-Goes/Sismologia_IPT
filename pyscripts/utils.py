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
import os
import xml.etree.ElementTree as ET


# ---------------------------- PARAMETROS -------------------------------------
# Nome da pasta mseed
PROJETO_DIR = "/home/ipt/projetos/Classificador_Sismologico"
mseed_folder = PROJETO_DIR + "/files/mseed"


# Dicionário de Netowrk ID
# MOHO IAG = https://www.moho.iag.usp.br/fdsnws/ -> 'USP'
ID_dict = {"MC": '8091',
           "IT": '8091',
           "SP": '8085',
           "PB": '8093',
           "BC": '8089',
           'USP': 'USP'}

# Delimitador para prints
delimt = "-------------------------------------------------\n"

# Caminho para diretório de invetário de redes sismológicas
path_inventario = './files/inventario/'
list_inventario = os.listdir(path_inventario)


# ---------------------------- FUNÇÕES ----------------------------------------
# Função para criar um dicionário a partir de um csv
def csv2list(csv_file, data=False):
    '''
    Recebe um csv e retorna uma lista de EventID
    evid é a primeira coluna do header do csv
    evid = usp0000XXXX
    Se data for uma ano (ex: 2022), retorna uma lista com eventos a partir do ano até hoje
    ex: data = 2010 -> retorna evid
    '''
    if data:
        with open(csv_file, 'r') as f:
            lines = f.readlines()
            evids = [line.split(',')[0] for line in lines[1:]]
            # split depois do usp, e pega só o ano '0000' e split o XXXXX as letras
            evid = [int(evid.split('usp')[1][:4]) for evid in evids]
            if evid < data:
                return None
            else:
                return evid
    else:
        with open(csv_file, 'r') as f:
            lines = f.readlines()
            return [line.split(',')[0] for line in lines[1:]]


# Função para ler um .txt e extrair o Netorw, Station e Latitute, Longitude e Depth e salvar  em um dicionário.
def cria_sta_dic(file, dic=None):
    '''
    Recebe:
        file: caminho do arquivo .txt com informações da rede sismológica
        dic: Dicionário possivelmente vazio ou com prévias informações de network, station, latitude, longitude e depth.

    Retorna:
        Dicionário com as informações de network, station, latitude, longitude e depth de cada estação.

    Exemplo de arquivo .txt:

    #Network|Station|Location|Channel|Latitude|Longitude|Elevation|Depth|Azimuth|Dip|SensorDescription|Scale|ScaleFreq|ScaleUnits|SampleRate|StartTime|EndTime
    BR|AGBLB||BHE|-9.03868|-37.045358|448.0|0.0|90.0|0.0|STS-2, 120 s, 1500 V/m/s, generation 1 electronics|936717000.0|0.05|M/S|40.0|2010-05-10T00:38:13.615|2012-09-14T00:44:13.24

    '''
    if not dic:
        dic = {}

    with open(file, 'r') as f:
        header = f.readline().strip().split('|')
        header = [h.replace('#', '') for h in header]
        idx_network = header.index('Network')
        idx_station = header.index('Station')
        idx_latitude = header.index('Latitude')
        idx_longitude = header.index('Longitude')
        idx_depth = header.index('Depth')

        for line in f:
            line = line.strip().split('|')
            network = line[idx_network]
            station = line[idx_station]
            latitude = float(line[idx_latitude])
            longitude = float(line[idx_longitude])
            depth = float(line[idx_depth])

            key = f"{network}.{station}"
            if key not in dic:
                dic[key] = []

            dic[key].append({
                'network': network,
                'station': station,
                'latitude': latitude,
                'longitude': longitude,
                'depth': depth
            })

    return dic


def get_inventory_from_xml(file, dic=None):
    '''
    Lê um arquivo XML e extrai informações da rede sismológica para atualizar ou criar um dicionário.

    Parâmetros:
        file: caminho para o arquivo XML com as informações da rede sismológica.
        dic: dicionário possivelmente vazio ou com informações prévias de network, station, latitude, longitude e depth.

    Retorna:
        Dicionário atualizado com as informações de network, station, latitude, longitude e depth de cada estação.
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
            elevation = station.find('ns:Elevation', ns).text  # Você pode precisar adaptar se a profundidade estiver em outra tag ou calcular com base na elevação, se aplicável.

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
                'depth': float(elevation)  # Assumindo que depth possa ser calculado ou igualado a elevation, ajuste conforme necessário.
            })
    return dic


# Função para pegar o a ('net.sta','lat','lon','depth') e retornar um dicionário com as informações
def get_sta_xy(net, sta, inventario):
    key = f"{net}.{sta}"
    if key in inventario:
        # Retorna a latitude e longitude encontradas no dicionário
        return inventario[key][0]['latitude'], inventario[key][0]['longitude']
    else:
        # Retorna None para ambos se a estação não for encontrada
        return None, None
