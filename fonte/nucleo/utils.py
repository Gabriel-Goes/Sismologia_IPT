# -*- coding: utf-8 -*-
# Python 3.10
# ./Classificador_Sismologico/source/Core/utils.py

# Autor: Gabriel Góes Rocha de Lima
# Funções de utilidade para Processar_Dados_Sismicos.py
# Versão: 0.2.1
# Data: 2024-02-27
# Modificação 2024-04-10

# ----------------------------  DESCRIPTION  ----------------------------------
# FUNÇÕES E VARIÁVEIS UTILITAŔIAS PARA O PROJETO
# Estas funções estão escritas aqui para melhorar a leitura dos scripts
# principais, aumentando a fluidez dos códigos deixando explícito apenas o que
# é realmente importante.

# ----------------------------  IMPORTS   -------------------------------------
from datetime import datetime
import os
import sys
from obspy.clients.fdsn.client import Client

# ---------------------------- PARAMETROS -------------------------------------
# Diretório do projeto
PROJETO_DIR = os.environ['HOME'] + "/projetos/ClassificadorSismologico"
# Nome da pasta mseed
MSEED_DIR = PROJETO_DIR + "/files/mseed"

# Clientes para acessar os dados
try:
    data_Client = Client('http://seisarc.sismo.iag.usp.br/')
except Exception as e:
    print(f'\nErro ao conectar com o servidor Seisarc.sismo.iag.usp.br: {e}')
    sys.exit(1)
data_Client_bkp = Client('http://rsbr.on.br:8081/fdsnws/dataselect/1/')

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
