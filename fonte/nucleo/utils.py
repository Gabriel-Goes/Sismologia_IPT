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

# ---------------------------- PARAMETROS -------------------------------------
PROJETO_DIR = os.environ['HOME'] + "/projetos/ClassificadorSismologico"
MSEED_DIR = PROJETO_DIR + "arquivos/mseed"
CAT_SNR = [
        '< 1', '[1-2[', '[2-3[', '[3-4[', '[4-5[', '[5-6[', '[6-7[', '[7-8[',
        '[8-9[', '[9-10[', '[10-11[', '[11-12[', '[12-13[', '[13-14[',
        '[14-15[', '>= 15'
]
CAT_DIS = [
            '< 25',
            '[25-50[',
            '[50-75[',
            '[75-100[',
            '[100-125[',
            '[125-150[',
            '[150-175[',
            '[175-200[',
            '[200-225[',
            '[225-250[',
            '[250-275[',
            '[275-300[',
            '[300-325[',
            '[325-350[',
            '>= 350'
        ]
CAT_MAG = [
        '<1', '[1-2[', '[2-3[', '>=3'
]
ID_dict = {"MC": '8091',
           "IT": '8091',
           "SP": '8085',
           "PB": '8093',
           "BC": '8089',
           'USP': 'USP'}

DELIMT = "-----------------------------------------------------\n"
DELIMT2 = "#####################################################\n"
BKP_TIME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# ---------------------------- FUNÇÕES ----------------------------------------
class DualOutput(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self,
              message: str) -> None:
        self.terminal.write(message)
        self.log.write(message)

    def flush(self) -> None:
        self.terminal.flush()
        self.log.flush()


def csv2list(csv_file: str, data=False) -> list:
    if data:
        evids = []
        with open(f'arquivos/catalogo/{csv_file}', 'r') as f:
            lines = f.readlines()
            evids_ = [line.split(',')[0] for line in lines[1:]]
        # parse  the fourth to seventh value of the evid
        for evid in evids_:
            if int(evid[3:7]) > int(data):
                evids.append(evid)
        return evids

    else:
        with open(f'arquivos/catalogo/{csv_file}', 'r') as f:
            lines = f.readlines()
            return [line.split(',')[0] for line in lines[1:]]
