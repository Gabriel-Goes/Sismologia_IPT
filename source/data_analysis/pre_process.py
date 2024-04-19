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
from data_analysis.test_filters import ratios
from data_analysis.test_filters import filterCombos
import pandas as pd
from obspy import UTCDateTime


# ----------------------------  FUNCTIONS  ------------------------------------
# ------------------------- SIGNAL NOISE RATIO ------------------------------- #
# Função para calcular SNR para um único arquivo mseed
def process_mseed_file(
        events: str) -> None:
    '''
    '''
    # Carrega o dataframe
    df = pd.read_csv(events)
    evento = df[:1]
    pick_time = UTCDateTime(evento['Pick Time'][0])


    # Carrega o arquivo mseed
    stream = read(evento['Path'][0])
    # Assume-se que o arquivo possui apenas uma trace ou processa a primeira
    trace = stream[0]
    # Define os filtros
    filtros = filterCombos(1., 35., 2., 12.)
    noisewindow = pick_time - 9, pick_time - 1
    pwindow = pick_time + 0.1, pick_time + 4
    swindow = 1, 1

    print(f"Pick time: {pick_time}")
    print(f'Noise window: {noisewindow}')
    print(f'P window: {pwindow}')
    print(f'S window: {swindow}')

    # Aplica a função ratios diretamente, já que get é para buscar de um cliente FDSN
    ratios(
        trace,
        filtros,
        noisewindow,
        pwindow,
        swindow
    )
'''

    try:
        pick_time = UTCDateTime(evento['Pick Time'][0])

        # Carrega o arquivo mseed
        stream = read(evento['Path'][0])
        # Assume-se que o arquivo possui apenas uma trace ou processa a primeira
        trace = stream[0]
        # Define os filtros
        filtros = filterCombos(1., 35., 2., 12.)
        noisewindow = pick_time - 9, pick_time - 1
        pwindow = pick_time + 0.1, pick_time + 4
        swindow = 1, 1

        print(f" -> Processing {evento['Event'][0]}\n")
        print(f"Pick time: {pick_time}")
        print(f'Noise window: {noisewindow}')
        print(f'P window: {pwindow}')
        print(f'S window: {swindow}')


        # Aplica a função ratios diretamente, já que get é para buscar de um cliente FDSN
        ratios(
            trace,
            filtros,
            noisewindow,
            pwindow,
            swindow
        )
        # Apenas para visualização ou conferência, mostramos alguma saída
        print(f"Processed {evento['Event']}")

        return filtros

    except Exception as e:
        print(f"Failed to process {evento['Event']}: {e}")
'''
