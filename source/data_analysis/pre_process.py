# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/pyscripts/ProcessarDadosSismologicos.py

# ----------------------------  DESCRIPTION  -----------------------------------
# Script para gerar catálogo de eventos sísmicos
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.2
# Data: 2024-02-27
# Modificação mais recente: 2024-04-10

# ----------------------------  IMPORTS   -------------------------------------
from obspy import read

# ----------------------------  FUNCTIONS  ------------------------------------
def sinal_ruido(mseed):
    """
    Calcula o ruído como a janela entre 1 e 9 segundos e o sinal como a janela
    entre 10 e 20 segundos.
    Função para calcular a relação sinal ruído
        Recebe:
            .mseed: arquivo de dados sísmicos.
        Retorna:
            Razão Sinal Ruído
    """
    st = read(mseed)
    sinal = st[0].data[1000:2000]
    ruido = st[0].data[100:900]
    return sum(sinal)/sum(ruido)
