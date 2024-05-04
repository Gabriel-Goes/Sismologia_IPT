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
import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as mtick
import seaborn as sns

import obspy
from obspy import UTCDateTime

from tqdm import tqdm

# from typing import List

from data_analysis.test_filters import parsewindow, filterCombos, prepare

# ----------------------------- DATA VIZ ------------------------------------ #


# ------------------------------ Functions ---------------------------------- #
def get_true_false(validation):
    df_val = pd.read_csv('files/output/' + validation)
    print(f' - non_comm_net: {df_val.shape}')

    ant_high_certainty = df_val[df_val['prob_ant'] > 0.75]
    nat_high_certainty = df_val[df_val['prob_ant'] < 0.25]

    return ant_high_certainty, nat_high_certainty


# ---------------------------- Plots ---------------------------------------- #
# Correlation Matrix
def plot_corr_matrix(df):
    cols = ['prob_nat', 'Hora',
            'Longitude', 'Latitude',
            'MLv', 'Distance', 'Num_Estacoes']
    df = df[cols]
    plt.figure(figsize=(10, 6))
    corr = df.corr()
    plt.matshow(corr, cmap='viridis', fignum=1,
                animated=True, interpolation='nearest')
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.colorbar()
    plt.title('Correlation Matrix')
    plt.tight_layout()
    plt.savefig('files/figures/corr_matrix.png')
    plt.show()


# --------------------------- ScatterPlots ---------------------------------- #
def plot_scatter(df, x, y):
    plt.figure(figsize=(10, 6))
    colors = ['b', 'r']
    shapes = ['o', 'x']
    for i, predict in enumerate(df['pred'].unique()):
        df_predict = df[df['pred'] == predict]
        plt.scatter(df_predict[x], df_predict[y],
                    color=colors[i], marker=shapes[i], alpha=0.5)
    plt.title('Scatter Plot')
    plt.xlabel(x)
    plt.ylabel(y)
    plt.tight_layout()
    plt.savefig('files/figures/scatter_plot.png')
    plt.show()


def plot_facetgrid(df, x, y, hue):
    df = df[['pred', 'prob_nat', 'Hora',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    g = sns.FacetGrid(df, hue=hue, height=5)
    g = g.map(plt.scatter, x, y, edgecolor="w").add_legend()
    plt.savefig('files/figures/facetgrid_scatter.png')
    plt.show()


def plot_pairplot(df):
    df = df[['pred', 'prob_nat', 'Hora',
             'MLv', 'Distance', 'Num_Estacoes']]
    sns.pairplot(df, hue='pred')
    plt.savefig('files/figures/pairplot.png')
    plt.show()


def plot_jointplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hora',
             'Longitude', 'Latitude', 'distance_category',
             'MLv', 'Distance', 'Num_Estacoes']]
    sns.jointplot(x=x, y=y, data=df, kind='scatter', hue='pred')
    plt.ylim(df[y].min() - 2, df[y].max() + 2)
    plt.xlim(df[x].min() - 0.5, df[x].max() + 0.5)
    plt.xticks(range(int(df[x].min()), int(df[x].max()) + 1))
    plt.yticks(range(int(df[y].min()), int(df[y].max()) + 1))
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.savefig('files/figures/jointplot.png')
    plt.show()


def plot_lmplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hora',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    sns.lmplot(x=x, y=y, data=df, hue='pred')
    plt.savefig('files/figures/lmplot.png')
    plt.show()


def plot_regplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hora',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    sns.regplot(x=x, y=y, data=df,)
    plt.savefig('files/figures/regplot.png')
    plt.show()


def plot_swarmplot(df, x, y, natural=True):
    df = df[['pred', 'prob_nat', 'Hora',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    if not natural:
        df = df[df['pred'] == 1]
        sns.swarmplot(x=x, y=y, data=df, size=2.5, color='red')
    else:
        sns.swarmplot(x=x, y=y, data=df, size=2.5, hue='pred')
    plt.savefig('files/figures/swarmplot.png')
    plt.show()


def plot_stripplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hora',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    sns.stripplot(x=x, y=y, data=df, size=2.5, hue='pred')
    plt.savefig('files/figures/stripplot.png')
    plt.show()


def plot_boxplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hora',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    sns.boxplot(x=x, y=y, data=df, hue='pred')
    plt.savefig('files/figures/boxplot.png')
    plt.show()


def plot_violinplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hora',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    sns.violinplot(x=x, y=y, data=df, hue='pred')
    plt.savefig('files/figures/violinplot.png')
    plt.show()


# ---------------------------- Histograms ----------------------------------- #
def plot_hist_kde(df, column):
    cols = ['prob_nat', 'Hora',
            'Longitude', 'Latitude',
            'MLv', 'Distance', 'Num_Estacoes']
    df = df[cols]
    sns.histplot(df[column], kde=True, color='lightskyblue')
    plt.title(f'Distribuição de {column}')
    plt.tight_layout()
    plt.savefig(f'files/figures/hist_kde_{column}.png')
    plt.show()


# --------------------------------- Hours
# Plot histogram of events hour distribution
def plot_hist_hour_distribution(df):
    df['Hora'] = df['Origin Time'].apply(lambda x: UTCDateTime(x).hour)
    counts = df['Hora'].value_counts(sort=False).reindex(
        np.arange(24),
        fill_value=0
    )
    density = counts / counts.sum()
    plt.figure(figsize=(10, 6))
    colors = ['blue' if (11 <= hour < 22) else 'red' for hour in counts.index]
    bars = plt.bar(counts.index, density, color=colors, alpha=0.5, width=0.8)

    for bar, label in zip(bars, counts):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2,
                 yval + 0.001, int(label), ha='center', va='bottom')

    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))

    plt.xticks(range(0, 24))
    plt.grid(axis='y')
    plt.title('Distribuição de eventos sísmicos por hora (UTC)')
    plt.xlabel('Hora (UTC)')
    plt.ylabel('Frequência')
    # Legenda: Commercial e Não-Comercial
    plt.legend(
        ['Horário Comercial',
         'Fora do Horário Comercial'],
        loc='upper right')
    # save figure
    plt.savefig('files/figures/pos_process/plots/histogramas/hist_hora.png')
    plt.show()


def plot_hist_hour_distribution_recall(df):
    # Converte 'Hora' em categorias cíclicas para melhor agrupamento e visualização
    df['Hora'] = pd.to_numeric(df['Hora'])
    df['Cat Hora'] = pd.cut(
        df['Hora'], bins=range(0, 25, 2), right=False, labels=range(0, 24, 2)
    )
    # Calcula a frequência relativa de cada categoria
    freq_relative = df['Cat Hora'].value_counts(normalize=True).sort_index()
    max_freq = freq_relative.max() * 100
    min_freq = freq_relative.min() * 100

    # Configura a coloração baseada na frequência
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    cmap = plt.cm.viridis
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Prepara o gráfico
    fig, ax = plt.subplots(figsize=(10, 6))

    # Itera sobre cada categoria para plotar
    for hour in freq_relative.index:
        hour_df = df[df['Cat Hora'] == hour]
        TP = hour_df[(hour_df['pred'] == 0) & (hour_df['label_cat'] == 0)].shape[0]
        FN = hour_df[(hour_df['pred'] == 1) & (hour_df['label_cat'] == 0)].shape[0]
        if TP + FN == 0:
            recall = 0  # Evita divisão por zero
        else:
            recall = TP / (TP + FN) * 100
        frequency = freq_relative.loc[hour] * 100
        color = cmap(norm(frequency))
        ax.bar(
            hour + 1,
            recall,
            color=color,
            edgecolor='black',
            width=2,
            align='center'
        )
        # Adiciona rótulos acima das barras
        ax.text(
            hour + 1,
            recall + 0.5,
            f'{recall:.2f}%',
            ha='center',
            va='bottom',
            color='black'
        )
    # Adiciona colorbar
    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    cbar.set_ticklabels([f'{min_freq:.2f}%', f'{max_freq:.2f}%'])

    # Configurações finais do plot
    plt.xticks(range(0, 24, 2), labels=[f'{h:02d}:00' for h in range(0, 24, 2)])
    plt.ylim(60, 100)
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray', axis='y')
    plt.title('Distribuição de Recall por Hora dos Eventos')
    plt.xlabel('Hora do Dia')
    plt.ylabel('Recall (%)')
    plt.tight_layout()

    # Opção para salvar ou mostrar o gráfico
    # plt.savefig('files/figures/hist_ev_hour_recall.png')
    plt.show()
    plt.close()

    return df

# --------------------------------- Distances
def plot_hist_distance_frequency(df):
    plt.figure(figsize=(10, 6))
    n, bins, patches = plt.hist(df['Distance'],
                                bins=range(50, 450, 50),
                                rwidth=0.8,
                                color='lightskyblue',
                                weights=np.zeros_like(df['Distance']) + 1. / df['Distance'].size)
    for freq, patch in zip(n, patches):
        freq = freq * 100
        plt.text(patch.get_x() + patch.get_width() / 2,
                 patch.get_height(),
                 f'{freq:.02f}%',
                 ha='center',
                 va='bottom')
    tick_positions = [x - 25 for x in range(50, 450, 50)]
    plt.xticks(tick_positions, [str(i) for i in range(50, 450, 50)])
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.title('Distribuição de Eventos por Distância Epicentral')
    plt.xlabel('Distância Epicentral (km)')
    plt.ylabel('Frequência Relativa')
    plt.savefig('files/figures/dist_ev_distance_rel_freq.png')
    plt.show()


# Classify distance categories
def classify_distance(distance):
    if distance < 50:
        return '<50'
    elif 50 <= distance < 100:
        return '[50-100['
    elif 100 <= distance < 150:
        return '[100-150['
    elif 150 <= distance < 200:
        return '[150-200['
    elif 200 <= distance < 250:
        return '[200-250['
    elif 250 <= distance < 300:
        return '[250-300['
    else:
        return '>=300'


# plot histogram of events distance distribution
def plot_hist_distance_recall(df):
    fig, ax = plt.subplots(figsize=(9, 6))
    categories = ['<50', '[50-100[', '[100-150[', '[150-200[', '[200-250[', '[250-300[', '>=300']
    df['distance_category'] = pd.Categorical(df['distance_category'],
                                             categories=categories,
                                             ordered=True)
    freq_relative = df['distance_category'].value_counts(normalize=True).sort_index()
    max_freq = freq_relative.max() * 100  # converte para porcentagem
    norm = mcolors.Normalize(vmin=0, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=norm)
    sm.set_array([])  # Array vazio para o ScalarMappable

    for category in categories:
        cat_df = df[df['distance_category'] == category]
        TP = cat_df[(cat_df['pred'] == 0) & (cat_df['label_cat'] == 0)].shape[0]
        FN = cat_df[(cat_df['pred'] == 1) & (cat_df['label_cat'] == 0)].shape[0]
        recall = TP / (TP + FN) * 100
        frequency = freq_relative.loc[category] * 100
        color = sm.to_rgba(frequency)
        ax.text(categories.index(category),
                recall + 0.01, f'{recall:.2f}',
                ha='center', va='bottom', color='black')
        ax.bar(category, recall, color=color)
    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    plt.ylim(65, 100)
    plt.xticks(range(len(categories)), categories)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.gca().xaxis.grid(False)
    # plt.title('Distance Distribution of Events')
    plt.xlabel('Epicentral Distance (km)')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('files/figures/hist_ev_distance.png')
    plt.show()
    plt.close()


# --------------------------   Magnitudes
def plot_hist_magnitude_distribution(df_merged):
    plt.figure(figsize=(10, 6))
    # Organiza o plot em ordem crescente de magnitude
    # >1, [1-2[, [2-3[, >=3
    df_merged['magnitude_category'] = pd.Categorical(df_merged['magnitude_category'],
                                                     categories=['<1', '[1-2[', '[2-3[', '>=3'],
                                                     ordered=True)
    df_merged['magnitude_category'].value_counts().sort_index().plot(kind='bar', color='lightskyblue')

    plt.title('Distribuição de Eventos por Categoria de Magnitude')
    plt.xlabel('Categoria de Magnitude')
    plt.ylabel('Número de Eventos')
    plt.tight_layout()
    plt.savefig('files/figures/dist_ev_cat_mag.png')
    plt.show()


def classify_magnitude(mag):
    if mag < 1:
        return '<1'
    elif 1 <= mag < 2:
        return '[1-2['
    elif 2 <= mag < 3:
        return '[2-3['
    else:
        return '>=3'


# Plot histogram of magnitude distribution by recall
# df_merged['pred'] and def_merged['nature']
def plot_hist_magnitude_distribution_recall(df_merged):
    fig, axis = plt.subplots(figsize=(10, 6))
    # Organiza o plot em ordem crescente de magnitude
    categories = ['<1', '[1-2[', '[2-3[', '>=3']
    df_merged['magnitude_category'] = pd.Categorical(df_merged['magnitude_category'],
                                                     categories=categories,
                                                     ordered=True)

    freq_relative = df_merged['magnitude_category'].value_counts(normalize=True).sort_index()
    max_freq = freq_relative.max() * 100

    norm = mcolors.Normalize(vmin=0, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=norm)
    sm.set_array([])

    for category in categories:
        mag_cat = df_merged[df_merged['magnitude_category'] == category]
        TP = mag_cat[(mag_cat['pred'] == 0) & (mag_cat['label_cat'] == 0)].shape[0]
        FN = mag_cat[(mag_cat['pred'] == 1) & (mag_cat['label_cat'] == 0)].shape[0]
        recall = TP / (TP + FN) * 100
        frequency = freq_relative.loc[category] * 100
        color = sm.to_rgba(frequency)
        # anotate at the top of the bar the recall value
        axis.text(categories.index(category),
                  recall + 0.01, f'{recall:.2f}',
                  ha='center', va='bottom', color='black')
        axis.bar(category, recall, color=color)

    cbar = fig.colorbar(sm, ax=axis)
    cbar.ax.set_ylabel('Frequency (%)')
    plt.xticks(range(len(categories)), categories)
    # Make the y axis start at 0.6
    plt.ylim(70, 100)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    # plt.title('Distribuição de Eventos por Categoria de Magnitude')
    plt.xlabel('Magnitude')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('files/figures/dist_ev_cat_mag_recall.png')
    plt.show()


# -------------------------- Number of Stations
def plot_hist_station_dist(df):
    plt.figure(figsize=(10, 6))
    # Histograma com frequências absolutas
    df['Num_Estacoes'].value_counts().sort_index().plot(
        kind='bar',
        color='lightskyblue'
    )
    # Anotate the top of the bar the frequency value
    for i, v in enumerate(df['Num_Estacoes'].value_counts().sort_index()):
        plt.text(i, v, str(v), ha='center', va='bottom', color='black')
    plt.xticks(
        range(len(df['Num_Estacoes'].unique())),
        df['Num_Estacoes'].unique()
    )
    # Adicionando gridlines horizontais
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.title('Distribuição de Eventos por Número de Estações')
    plt.xlabel('Número de Estações')
    plt.ylabel('Número de Eventos')
    plt.tight_layout()
    plt.savefig('files/figures/dist_ev_num_stations_absoluto.png')
    plt.show()


def plot_hist_num_stations_recall(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    stat_cat = df['Num_Estacoes'].unique()
    stat_cat.sort()
    df['Station_Category'] = pd.Categorical(df['Num_Estacoes'],
                                            categories=stat_cat,
                                            ordered=True)
    freq_relative = df['Station_Category'].value_counts(normalize=True).sort_index()
    max_freq = freq_relative.max() * 100
    norm = mcolors.Normalize(vmin=0, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=norm)
    sm.set_array([])
    for stations in stat_cat:
        stat_cat_df = df[df['Station_Category'] == stations]
        TP = stat_cat_df[(stat_cat_df['pred'] == 0) & (stat_cat_df['label_cat'] == 0)].shape[0]
        FN = stat_cat_df[(stat_cat_df['pred'] == 1) & (stat_cat_df['label_cat'] == 0)].shape[0]
        recall = TP / (TP + FN) * 100
        frequency = freq_relative.loc[stations] * 100
        color = sm.to_rgba(frequency)
        # anotate at the top of the bar the recall value
        ax.text(stat_cat_df['Station_Category'].cat.categories.get_loc(stations),
                recall + 0.01, f'{recall:.2f}',
                ha='center', va='bottom', color='black')
        ax.bar(stat_cat_df['Station_Category'].cat.categories.get_loc(stations),
               recall, color=color)
    cbar = plt.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    plt.xticks(range(len(stat_cat)), stat_cat)
    plt.ylim(70, 110)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.title('Distribuição de Eventos por Número de Estações')
    plt.xlabel('Número de Estações')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('files/figures/dist_ev_num_stations_recall.png')
    plt.show()


def snr_p(picks: pd.DataFrame,
          window: int) -> [pd.DataFrame, dict]:
    '''
    Program main body
    This function gets a dataframe with all information about the picked event.

    Index(['ID', 'Event', 'Error', 'Pick', 'Network', 'Station', 'Location',
           'Channel', 'Latitude', 'Longitude', 'Distance', 'Start Time',
           'End Time', 'Pick Time', 'Origin Time', 'Origem Latitude',
           'Origem Longitude', 'Cat', 'Stream Count', 'Hora de Origem (UTC)',
           'MLv', 'Certainty', 'Path', 'Event.1'],
          dtype='object')

    the program will parse through the dataframe and execute the analysis for
    each pick.
    '''
    for index, pick in tqdm(picks.iterrows()):
        # Get the network, station, location and channel codes
        nw = str(obspy.UTCDateTime(pick['Pick Time']) - 9) + '/8'
        pw = str(obspy.UTCDateTime(pick['Pick Time'])) + '/' + str(window)
        sw = str(obspy.UTCDateTime(pick['Pick Time']) + 20) + '/5'

        # Create the windows
        noisewindow = parsewindow(nw)
        pwindow = parsewindow(pw)
        swindow = parsewindow(sw)

        # Get the trace from dataframe
        st = obspy.read(pick['Path'])
        trace = st[0]

        # Get the filter combinations
        filtros = filterCombos(1., 49., 4., 49.)
        dict_filtros = {f'{filtro.pa}_{filtro.pb}': filtro for filtro in filtros}
        filtro_bom = dict_filtros['2.0_49.0']
        noise, trace_p, trace_s = prepare(
            trace,
            filtro_bom,
            noisewindow, pwindow, swindow)

        filtro_bom.noise = np.mean(np.abs(noise))
        filtro_bom.p = np.mean(np.abs(trace_p))
        filtro_bom.s = np.mean(np.abs(trace_s))
        filtro_bom.snrp = filtro_bom.p / filtro_bom.noise
        filtro_bom.snrs = filtro_bom.s / filtro_bom.noise

        picks.at[index, 'SNR_P'] = filtro_bom.snrp
        picks.at[index, 'Noise'] = filtro_bom.noise
        picks.at[index, 'p'] = filtro_bom.p

    return picks, dict_filtros


# --------------------------- Create files
def load_data():
    # Load the validation network level
    try:
        events = pd.read_csv('files/events/events.csv')
    # If file does not exist
    except Exception as e:
        print(f'Error: {e}')
        # Open the most recent file of the 'files/events/.bkp/' directory
        ev_bkp = sorted(os.listdir('files/events/.bkp/'))[-1]
        print(f'Loaded the most recent bkp file: {ev_bkp}')
        # Ask if want to continue
        if input('Do you want to continue? (y/n)') == 'n':
            return
        events = pd.read_csv('files/events/.bkp/' + ev_bkp)

    events['file_name'] = events['Path'].apply(
        lambda x: x.split('/')[-1].split('.')[0]
    )
    df_ncomm_val = pd.read_csv('files/output/no_commercial/validation_station_level.csv')
    df_comm_val = pd.read_csv('files/output/commercial/validation_station_level.csv')

    df_nc = pd.merge(df_ncomm_val, events, on='file_name', how='left')
    df_comm = pd.merge(df_comm_val, events, on='file_name', how='left')

    df_nc.set_index(['Event', 'Station'], inplace=True)

    return df_nc, df_comm, events, df_ncomm_val, df_comm_val


def non_commercial(df):
    plot_hist_hour_distribution(df)
    plot_hist_hour_distribution_recall(df)
    plot_hist_station_dist(df)
    plot_hist_num_stations_recall(df)

    # Histogram - Frequency of Distances ( nearest station of event)
    plot_hist_distance_frequency(df)

    # Histograma mergeddistancia
    df.loc[:, 'distance_category'] =\
        df['Distance'].apply(classify_distance)

    plot_hist_distance_recall(df)

    # histograma categoria de magnitude por recall
    df.loc[:, 'magnitude_category'] =\
        df['MLv'].apply(classify_magnitude)

    plot_hist_magnitude_distribution_recall(df)

    return


# -------------------------------- Main -------------------------------------- #
def main():
    x = load_data()
    df_nc = x[0]
    picks, dict_filtros = snr_p(df_nc, 5)


    non_commercial(df_nc)

    return x, picks, dict_filtros, df_nc


if __name__ == '__main__':
    main()
