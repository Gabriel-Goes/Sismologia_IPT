# -*- coding: utf-8 -*-
# Python 3.11.9
# ./Classificador_Sismologico/pyscripts/BaixarFormaOnda.py


# ----------------------------  DESCRIPTION  -----------------------------------
# Script criar um inventário de estações a partir de arquivos XML e TXT
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.1.0
# Data: 2024-04-15
# Modificado: 2024-04-15


# ----------------------------  IMPORTS   -------------------------------------
from lxml import etree
import xml.etree.ElementTree as ET
import pandas as pd


# Tentativa de inspeção detalhada da estrutura dos arquivos XML
def inspect_xml_structure(file_path):
    try:
        tree = etree.parse(file_path)
        root = tree.getroot()
        print(f"Root tag: {root.tag}")
        print(f"Root attributes: {root.attrib}")

        # Print the first few child elements to understand the structure
        for i, child in enumerate(root.iter()):
            print(f"Element tag: {child.tag}, Element text: {child.text}")
            if i > 10:  # Limit the output to the first 10 elements
                break
    except Exception as e:
        print(f"Error reading XML structure: {e}")


def process_xml_to_csv(xml_path, csv_path):
    """
    Processa um arquivo XML de estações sismológicas e sensores para criar um dataframe.

    Args:
    xml_path (str): Caminho para o arquivo XML de entrada.
    """
    # Carregar e parsear o XML
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Lista para armazenar os dados extraídos
    data = []
    # Criar um DataFrame
    df = pd.DataFrame(data)

    # Iterar sobre os elementos do XML
    for station in root.iter("Station"):
        # Extrair os dados da estação
        station_data = {
            "StationCode": station.find("StationCode").text,
            "StationName": station.find("StationName").text,
            "Latitude": station.find("Latitude").text,
            "Longitude": station.find("Longitude").text,
            "Elevation": station.find("Elevation").text,
        }
        # Adicionar os dados da estação ao DataFrame
        df = df.append(station_data, ignore_index=True)

    # Exportar para CSV
    # df.to_csv(csv_path, index=False)

    print(f"Data successfully saved to {csv_path}")

    return df
