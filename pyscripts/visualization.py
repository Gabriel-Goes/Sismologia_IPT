#!/usr/bin/env python
# coding: utf-8

# import sys
import matplotlib.pyplot as plt

import numpy as np
from numpy import moveaxis
import os
import pandas as pd
# from math import sqrt

from ipywidgets import interactive
# from ipywidgets import FloatSlider
# from ipywidgets import Dropdown
import ipywidgets as widgets

import obspy as op
# from obspy.signal.trigger import plot_trigger
# from obspy.signal.trigger import classic_sta_lta
# from obspy.signal.trigger import trigger_onset


# ---------------------------------------------------------------------------- #
files_path = '/home/ipt/projetos/Classificador_Sismologico/files/'


# # Visualization of a record and the prediction associated
pred_net = pd.read_csv(files_path + "output/non_commercial/validation_network_level.csv")
stream_c = None
stream = None
pred_net


pred_sta = pd.read_csv(files_path + "output/non_commercial/validation_station_level.csv")
stream_c = None
stream = None
pred_sta


df = pred_net
# df = pred_sta

# Dropdown para escolha do evento
dropdown_event = widgets.Dropdown(description='Eventos')
dropdown_event.options = df['event'].unique()  # Change to df['file_name'].unique() if using pred_net
dropdown_event.value = dropdown_event.options[0]

dropdown_station = widgets.Dropdown(description='Estações')

dropdown_network = widgets.Dropdown(description='Redes')


def get_event_folder(row):
    """
    Determina a pasta do evento baseada na linha do DataFrame.
    Se a linha contiver 'file_name', extrai a informação de lá.
    Caso contrário, usa a coluna 'event'.
    """
    if 'file_name' in row:
        return row['file_name'].split('_')[-1]  # Extrai EVENTTIME de NET_STA_EVENTTIME
    else:
        return row['event']  # Usa diretamente o EVENTTIME


# Função para ordenar e filtrar eventos com base na probabilidade antropogênica
def get_filtered_events(label_cat, nature, prob_order):
    filtered_df = df[(df['label_cat'] == label_cat) & (df['nature'] == nature)]
    if prob_order == 'Alta':
        filtered_df = filtered_df.sort_values(by='prob_ant', ascending=False)
    else:
        filtered_df = filtered_df.sort_values(by='prob_ant', ascending=True)
    return filtered_df['event'].tolist()


# Função para obter as estações e redes disponíveis para um determinado evento
def get_stations_and_networks(event_folder):
    stations = set()
    networks = set()
    for file in os.listdir(event_folder):
        if file.endswith(".mseed"):
            parts = file.split('_')
            network = parts[0]
            station = parts[1]
            networks.add(network)
            stations.add(station)
        else:
            print("Erro")
    print(list(stations))
    print(list(networks))

    return list(networks), list(stations)


# Função para atualizar as estações e redes disponíveis com base no evento selecionado
def update_stations_and_networks(event):
    event_folder = f'{files_path}mseed/{event}'
    networks, stations = get_stations_and_networks(event_folder)
    dropdown_network.options = networks
    dropdown_station.options = stations
    dropdown_station.value = dropdown_station.options[0]
    dropdown_network.value = dropdown_network.options[0]




# Função para atualizar a lista de eventos com base nos critérios selecionados
def update_event_list(*args):
    filtered_events = get_filtered_events(label_cat_selector.value, nature_selector.value, prob_order_selector.value)
    dropdown_event.options = filtered_events


# Função para plotar o evento selecionado
def plot_interativo(event, station, network, freqmin, freqmax):
    if freqmin < freqmax:
        global stream_c
        global stream
        try:
            stream = op.read(f'{files_path}mseed/{event}/{network}_{station}_{event}.mseed')
            stream_c = stream.copy()
            stream_c.detrend('demean')
            stream_c.taper(0.05)
            stream_c.filter('bandpass', freqmin=freqmin, freqmax=freqmax, corners=4, zerophase=True)
            print(stream_c)
            time = stream_c[0].times()
            trZ = stream_c.select(component='Z')[0].data
            # Criação do plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(24, 9))  # Ajuste o tamanho conforme necessário

            ax1.plot(time, trZ, color='black', linewidth=0.5, label='HH*')
            ax1.set_ylabel('Counts', fontsize=16)
            ax1.set_xlabel('Time [sec]', fontsize=16)
            ax1.set_xlim(time.min(), time.max())
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.tick_params(labelsize=14)
            ax1.legend()

            prob_ant = df.loc[df['event'] == event, 'prob_ant'].values[0]
            if df.loc[df['event'] == event, 'label_cat'].values[0] == 0:
                rotulo = "Natural"
                # Se for Natural, mas a probabilidade de ser Antropogênico for maior que 0.5, cor = vermelho
                text_color = 'red' if prob_ant > 0.5 else 'black'
            else:
                rotulo = "Antropogênico"
                # Se for Antropogênico, mas a probabilidade de ser Antropogênico for menor que 0.5, cor = vermelho
                text_color = 'red' if prob_ant < 0.5 else 'black'

            ax1.text(0.05, 0.95, s=f'{network}_{station}_{event}', transform=ax1.transAxes)
            ax1.text(0.05, 0.85, f'Rótulo: {rotulo}', transform=ax1.transAxes, color=text_color)
            ax1.text(0.05, 0.80, f'Prob Antrópico: {prob_ant*100} %', transform=ax1.transAxes, color=text_color)
            ax1.text(0.05, 0.75, f'Frequência mínima: {freqmin}', transform=ax1.transAxes)
            ax1.text(0.05, 0.70, f'Frequência máxima: {freqmax}', transform=ax1.transAxes)

            print(event)
            spectrogram = np.load(f'{files_path}spectro/{event}/{network}_{station}_{event}.npy', allow_pickle=True)
            spectro = moveaxis(spectrogram, 0, 2)

            freqs = list(range(1, 51))
            time = list(np.arange(0.5, 59.75, 0.25))
            nyquist_f = 50.0
            fig = plt.figure(figsize=(29, 12))
            psd = spectro.copy()

            # Compute the grid and get the data to plot on
            T, F = np.meshgrid(time, freqs)
            psd_mat = np.array(psd[:, :, 0])

            # Define the colormap
            cmap = plt.get_cmap('BuPu')

            # Create Axes from a given Figure
            ax2.pcolormesh(T, F, psd_mat.T, vmin=0, vmax=0.5, cmap=cmap, shading='gouraud', label='HH*')
            #ax_cbar = fig.add_axes([0.81, 0.8, 0.01, 0.35])  # colorbar

            # Plot the spectrogram
            plot_spectro = ax2.pcolormesh(T, F, psd_mat.T,
                                                vmin=0, vmax=0.5,
                                                cmap=cmap, shading='gouraud', label='HHZ')

            # Beautify spectrogram
            ax2.set_xlim((0.0, 60.0))
            ax2.set_ylabel('Frequency [Hz]', fontsize=16)
            ax2.set_xlabel('Time [s]', fontsize=16)
            ax2.tick_params(labelsize = 14)

            # Plot text as legend
            ax2.text(x=59, y=47, s=f'{stream_c[0].stats.component}',
                            color='black', fontsize=16)#, weight='bold')

            get_stations_and_networks(files_path + 'mseed/' + str(event))
            plt.tight_layout()  # Ajusta automaticamente o layout
            plt.show()
        except Exception as e:
            print(f' Error: {e}')

    else:
        print("A frequência mínima deve ser menor que a frequência máxima")


# Inicializar as opções de estação e rede para o primeiro evento
update_stations_and_networks(dropdown_event.options[0])


# Adicionar observador ao dropdown_event para atualizar as estações e redes disponíveis
dropdown_event.observe(lambda change: update_stations_and_networks(change.new), 'value')


# Widgets para seleção dos critérios de filtro
label_cat_selector = widgets.Dropdown(options=df['label_cat'].unique(), description='Label Cat')
nature_selector = widgets.Dropdown(options=df['nature'].unique(), description='Predito')
prob_order_selector = widgets.Dropdown(options=['Alta', 'Baixa'], description='Prob Antropogênica')


# Observadores para atualizar os eventos quando os critérios mudam
label_cat_selector.observe(update_event_list, 'value')
nature_selector.observe(update_event_list, 'value')
prob_order_selector.observe(update_event_list, 'value')


# Inicialize a lista de eventos
update_event_list()


# Criação do plot interativo
slider_freqmin = widgets.FloatSlider(value=5, min=1, max=49, step=1, description='Freq Min', continuous_update=False)
slider_freqmax = widgets.FloatSlider(value=35, min=2, max=50, step=1, description='Freq Max', continuous_update=False)
interactive_plot = interactive(plot_interativo, event=dropdown_event, station=dropdown_station, network=dropdown_network, freqmin=slider_freqmin, freqmax=slider_freqmax)


# Exibição dos widgets e do plot interativo
widgets.VBox([label_cat_selector, nature_selector, prob_order_selector, interactive_plot])
