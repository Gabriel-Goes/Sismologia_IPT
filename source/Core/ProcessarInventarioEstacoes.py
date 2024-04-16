# -*- coding: utf-8 -*-
# Python 3.11.9
# ./source/Core/ProcessarInventarioEstacoes.py


# ----------------------------  DESCRIPTION  ----------------------------------
# Script criar um inventário de estações a partir de um Client FDSNWS com obspy
# e salva em um arquivo xml ou outro formato.
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.1.0
# Data: 2024-04-15
# Modificado: 2024-04-15


# ----------------------------  IMPORTS   -------------------------------------
from Core.utils import data_Client


# ----------------------------  CONSTANTS  ------------------------------------
inv = data_Client.get_stations(network='BR',
                               station='*',
                               channel='*')

coords = inv.get_coordinates('BR')

# ----------------------------  FUNCTIONS  ------------------------------------
# Função para criar um xml de inventário de estações com base em um Client FDSNWS


# ----------------------------  MAIN  -----------------------------------------
if __name__ == '__main__':
    print(inv)
    print(coords)
    print('Fim do script')
