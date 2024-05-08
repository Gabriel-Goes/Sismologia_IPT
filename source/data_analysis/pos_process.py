# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/pyscripts/ProcessarDadosSismologicos.py

# ----------------------------  DESCRIPTION  ----------------------------------
# Script para gerar catálogo de eventos sísmicos
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.2
# Data: 2024-02-27
# Modificação mais recente: 2024-04-10

# ----------------------------  IMPORTS   -------------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as mtick
from matplotlib.cm import ScalarMappable
import seaborn as sns

import obspy

from shapely.geometry import Point
import geopandas as gpd

from tqdm import tqdm
from data_analysis.test_filters import parsewindow, filterCombos, prepare


# ----------------------------- DATA VIZ ------------------------------------ #
# ------------------------------ Functions ---------------------------------- #
def plot_box_dist(df):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    sns.histplot(
        df[df['nature'] == 'Natural']['prob_nat'],
        bins=20, kde=True, ax=axes[0], color='blue'
    )
    axes[0].set_title('Distribuição de prob_nat para Eventos Naturais')
    sns.histplot(
        df[df['nature'] == 'Anthropogenic']['prob_nat'],
        bins=20, kde=True, ax=axes[1], color='red'
    )
    axes[1].set_title('Distribuição de prob_nat para Eventos Antrópicos')
    sns.boxplot(x='nature', y='Distance', data=df, ax=axes[2])
    axes[2].set_title('Boxplot da Distância por Natureza do Evento')
    plt.savefig('files/figures/pos_process/boxplot_dist.png')
    plt.show()


def plot_box_by_network(df):
    df = df.reset_index()
    stations = df['Network'].unique()
    freq_rel = df['Network'].value_counts(normalize=True)
    norm = plt.Normalize(freq_rel.min(), freq_rel.max())
    cmap = sns.cubehelix_palette(
        dark=.25, light=.75, start=.5, rot=-.75, as_cmap=True
    )
    station_colors = {
        station: cmap(norm(freq_rel[station])) for station in stations
    }
    plt.figure(figsize=(27, 9))
    ax = plt.gca()
    sns.boxplot(
        x='Network', y='prob_nat',
        data=df, palette=station_colors, showfliers=False
    )
    sns.stripplot(
        x='Network', y='prob_nat',
        data=df, color='black', size=1, jitter=True, alpha=0.5
    )
    plt.title('Boxplot da Probabilidade Natural por Rede')
    plt.xlabel('Rede')
    plt.ylabel('Probabilidade Natural')
    plt.xticks(rotation=45)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical')
    cbar.set_label(f'Frequência Relativa - Total de Eventos: {df.shape[0]}')
    cbar.set_ticks([freq_rel.min(), freq_rel.max()])
    cbar.set_ticklabels([f'{freq_rel.min():.2f}', f'{freq_rel.max():.2f}'])
    plt.savefig('files/figures/pos_process/boxplot_rede.png')

    plt.show()


def plot_box_by_station(df):
    df = df.reset_index()
    cmap = sns.cubehelix_palette(
        dark=.25, light=.75, start=.5, rot=-.75, as_cmap=True)
    networks = df['Network'].unique()

    for network in networks:
        network_data = df[df['Network'] == network]
        freq_rel = network_data['Station'].value_counts(normalize=True)
        norm = plt.Normalize(freq_rel.min(), freq_rel.max())
        station_colors = {
            station: cmap(
                norm(freq_rel[station])
            ) for station in network_data['Station'].unique()
        }
        plt.figure(figsize=(10, 6))
        ax = sns.boxplot(
            x='Station', y='prob_nat',
            data=network_data, palette=station_colors, showfliers=False
        )
        ax = sns.stripplot(
            x='Station', y='prob_nat',
            data=network_data, color='red', jitter=True, size=1.5, alpha=0.5
        )
        ax.set_title(
            f'Probabilidade Natural por Estação para a Rede {network}'
        )
        ax.set_xlabel('Estação')
        ax.set_ylabel('Probabilidade Natural')
        plt.xticks(rotation=45)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, orientation='vertical', ax=ax)
        cbar.set_label(f'Frequência Relativa (Total: {network_data.shape[0]})')
        ticks = np.linspace(0, 1, num=5)
        cbar.set_ticks(ticks)
        cbar.set_ticklabels([f'{norm(t) * 100:.0f}%' for t in ticks])

        plt.savefig(f'files/figures/pos_process/boxplot_{network}.png')
        plt.show()


# Correlation Matrix
def plot_corr_matrix(df):
    cols = ['prob_nat', 'Hora',
            'Longitude', 'Latitude', 'Origem Latitude', 'Origem Longitude',
            'MLv', 'Distance', 'SNR_P']
    df = df[cols]
    plt.figure(figsize=(10, 6))
    corr = df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr, mask=mask, cmap='RdBu', annot=True, fmt='.2f', square=True,
        center=0, linewidths=0.5, linecolor='black'
    )
    plt.title('Correlation Matrix')
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/corr_matrix.png')
    plt.show()


# --------------------------- ScatterPlots ---------------------------------- #
def plot_scatter(df, x, y):
    plt.figure(figsize=(10, 6))
    colors = ['b', 'r']
    shapes = ['o', 'x']
    for i, p in enumerate(df['pred'].unique()):
        df_pred = df[df['pred'] == p]
        plt.scatter(df_pred[x], df_pred[y],
                    color=colors[i], marker=shapes[i], alpha=0.5)
    plt.title('Scatter Plot')
    plt.xlabel(x)
    plt.ylabel(y)
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/scatter_plot.png')
    plt.show()


def plot_pairplot(df):
    df = df[['pred', 'prob_nat', 'Hora',
             'MLv', 'Distance', 'Num_Estacoes']]
    sns.pairplot(df, hue='pred')
    plt.savefig('files/figures/pos_process/pairplot.png')
    plt.show()


def plot_swarmplot(df, x, y, natural=True):
    df = df[['pred', 'prob_nat', 'Hora',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    if not natural:
        df = df[df['pred'] == 1]
        sns.swarmplot(x=x, y=y, data=df, size=2.5, color='red')
    else:
        sns.swarmplot(x=x, y=y, data=df, size=2.5, hue='pred')
    plt.savefig('files/figures/pos_process/swarmplot.png')
    plt.show()


# ---------------------------- Histograms ----------------------------------- #
# --------------------------------- Probabilities
def class_prob(prob):
    if prob < 0.2:
        return '<0.2'
    elif 0.2 <= prob < 0.4:
        return '[0.2-0.4['
    elif 0.4 <= prob < 0.6:
        return '[0.4-0.6['
    elif 0.6 <= prob < 0.8:
        return '[0.6-0.8['
    elif 0.8 <= prob < 0.9:
        return '[0.8-0.9['
    else:
        return '>=0.9'


def plot_hist_prob_distribution(df):
    plt.figure(figsize=(10, 6))
    df['prob_nat'].plot(kind='hist', bins=20, color='lightskyblue')
    plt.title('Distribuição de Probabilidades Naturais')
    plt.xlabel('Probabilidade Natural')
    plt.ylabel('Frequência')
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/dist_prob_nat.png')
    plt.show()


def plot_hist_prob_recall(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    cat = ['<0.2', '[0.2-0.4[', '[0.4-0.6[', '[0.6-0.8[', '[0.8-0.9[', '>=0.9']
    df['prob_nat_cat'] = pd.Categorical(
        df['prob_nat_cat'], categories=cat, ordered=True
    )
    f_rel = df['prob_nat_cat'].value_counts(normalize=True).sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    rc_min = 0

    for c in f_rel.index:
        df_c = df[df['prob_nat_cat'] == c]
        TP = df_c[(df_c['pred'] == 0) & (df_c['label_cat'] == 0)].shape[0]
        FN = df_c[(df_c['pred'] == 1) & (df_c['label_cat'] == 0)].shape[0]
        rc = TP / (TP + FN) * 100
        freq = f_rel.loc[c] * 100
        color = sm.to_rgba(freq)
        ax.bar(c, rc, color=color, edgecolor='black', width=0.5)
        ax.text(c, rc + 0.01, f'{rc:.2f}%', ha='center', va='bottom')
        rc_min = rc if rc < rc_min else rc_min

    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    plt.ylim(rc_min - 5, 100)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xlabel('Probabilidade Natural')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/dist_prob_nat_recall.png')
    plt.show()


# --------------------------------- Hours
# Plot histogram of events hour distribution
def plot_hist_hour_distribution(df):
    counts = df['Hora'].value_counts(sort=False).reindex(
        np.arange(24),
        fill_value=0
    )
    density = counts / counts.sum()
    plt.figure(figsize=(10, 6))
    colors = ['blue' if (11 <= hour < 22) else 'red' for hour in counts.index]
    bars = plt.bar(counts.index, density, color=colors, alpha=0.5, width=0.8)

    for b, l in zip(bars, counts):
        yval = b.get_height()
        plt.text(b.get_x() + b.get_width() / 2,
                 yval + 0.001, int(l), ha='center', va='bottom')

    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    plt.xticks(range(0, 24))
    plt.grid(axis='y')
    plt.title('Distribuição de eventos sísmicos por hora (UTC)')
    plt.xlabel('Hora (UTC)')
    plt.ylabel('Frequência')
    # Legenda: Commercial e Não-Comercial
    plt.legend(['Não-Comercial'], loc='upper right')
    # save figure
    plt.savefig(
        'files/figures/pos_process/pos_process/plots/histogramas/hist_hora.png'
    )
    plt.show()


def plot_hist_hour_recall(df):
    df['Hora'] = pd.to_numeric(df['Hora'])
    df['Cat Hora'] = pd.cut(
        df['Hora'], bins=range(0, 25, 1), right=False, labels=range(0, 24, 1)
    )
    f_rel = df['Cat Hora'].value_counts(normalize=True).sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    cmap = plt.cm.magma
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    fig, ax = plt.subplots(figsize=(14, 8))
    for h in f_rel.index:
        h_df = df[df['Cat Hora'] == h]
        TP = h_df[(h_df['pred'] == 0) & (h_df['label_cat'] == 0)].shape[0]
        FN = h_df[(h_df['pred'] == 1) & (h_df['label_cat'] == 0)].shape[0]
        if TP + FN == 0:
            rc = 0
        else:
            rc = TP / (TP + FN) * 100
        freq = f_rel.loc[h] * 100
        cor = cmap(norm(freq))
        ax.bar(
            h, rc, color=cor, edgecolor='black', width=0.5, align='center'
        )
        ax.text(
            h, rc + 0.5, f'{rc:.0f}%', ha='center', va='bottom', color='black'
        )
    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    cbar.set_ticklabels([f'{min_freq:.2f}%', f'{max_freq:.2f}%'])
    plt.xticks(range(0, 24, 1), labels=[f'{h}h' for h in range(0, 24, 1)])
    plt.ylim(60, 100)
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray', axis='y')
    plt.title('Distribuição de Recall por Hora dos Eventos')
    plt.xlabel('Hora do Dia')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/hist_ev_hour_recall.png')
    plt.show()
    plt.close()


# --------------------------------- Distances
# Classify distance categories
def class_dist(dist):
    if dist < 50:
        return '<50'
    elif 50 <= dist < 100:
        return '[50-100['
    elif 100 <= dist < 150:
        return '[100-150['
    elif 150 <= dist < 200:
        return '[150-200['
    elif 200 <= dist < 250:
        return '[200-250['
    elif 250 <= dist < 300:
        return '[250-300['
    else:
        return '>=300'


def plot_hist_distance_distribution(df):
    n, bins, patches = plt.hist(
        df['Distance'],
        bins=range(50, 450, 50),
        rwidth=0.8,
        color='lightskyblue',
        weights=np.zeros_like(df['Distance']) + 1. / df['Distance'].size
    )
    plt.figure(figsize=(10, 6))
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
    plt.savefig('files/figures/pos_process/dist_ev_distance_rel_freq.png')
    plt.show()


# plot histogram of events distance distribution
def plot_hist_distance_recall(df):
    cat = [
        '<50',
        '[50-100[',
        '[100-150[',
        '[150-200[',
        '[200-250[',
        '[250-300[',
        '>=300'
    ]
    df['Distance_cat'] = pd.Categorical(
        df['Distance_cat'], categories=cat, ordered=True
    )
    f_rel = df['Distance_cat'].value_counts(normalize=True).sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    fig, ax = plt.subplots(figsize=(9, 6))

    for c in f_rel.index:
        c_df = df[df['Distance_cat'] == c]
        TP = c_df[(c_df['pred'] == 0) & (c_df['label_cat'] == 0)].shape[0]
        FN = c_df[(c_df['pred'] == 1) & (c_df['label_cat'] == 0)].shape[0]
        rc = TP / (TP + FN) * 100
        freq = f_rel.loc[c] * 100
        color = sm.to_rgba(freq)
        ax.bar(c, rc, color=color, edgecolor='black', width=0.5)
        ax.text(c, rc + 0.5, f'{rc:.2f}', ha='center', va='bottom')

    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, f_rel.mean() * 100, max_freq])
    plt.xticks(np.arange(len(f_rel.index)), labels=f_rel.index)
    plt.ylim(50, 100)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.gca().xaxis.grid(False)
    plt.xlabel('Epicentral Distance (km)')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/hist_ev_distance.png')
    plt.show()
    plt.close()


# --------------------------   Magnitudes
def class_mag(mag):
    if mag < 1:
        return '<1'
    elif 1 <= mag < 2:
        return '[1-2['
    elif 2 <= mag < 3:
        return '[2-3['
    else:
        return '>=3'


def plot_hist_magnitude_distribution(df):
    plt.figure(figsize=(10, 6))
    df['Magnitude_cat'] = pd.Categorical(
        df['Magnitude_cat'],
        categories=['<1', '[1-2[', '[2-3[', '>=3'],
        ordered=True
    )
    df['Magnitude_cat'].value_counts().sort_index().plot(
        kind='bar', color='lightskyblue'
    )
    plt.title('Distribuição de Eventos por Categoria de Magnitude')
    plt.xlabel('Categoria de Magnitude')
    plt.ylabel('Número de Eventos')
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/dist_ev_cat_mag.png')
    plt.show()


def plot_hist_magnitude_recall(df):
    fig, axis = plt.subplots(figsize=(10, 6))
    cat = ['<1', '[1-2[', '[2-3[', '>=3']
    df['Magnitude_cat'] = pd.Categorical(
        df['Magnitude_cat'], categories=cat, ordered=True
    )
    f_rel = df['Magnitude_cat'].value_counts(normalize=True).sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=0, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    rc_min = 0

    for c in f_rel.index:
        df_c = df[df['Magnitude_cat'] == c]
        TP = df_c[(df_c['pred'] == 0) & (df_c['label_cat'] == 0)].shape[0]
        FN = df_c[(df_c['pred'] == 1) & (df_c['label_cat'] == 0)].shape[0]
        rc = 100 * TP / (TP + FN) if TP + FN != 0 else 0
        freq = f_rel.loc[c] * 100
        color = sm.to_rgba(freq)
        axis.bar(c, rc, color=color, edgecolor='black', width=0.5)
        axis.text(c, rc + 0.01, f'{rc:.2f}%', ha='center', va='bottom')
        rc_min = rc if rc < rc_min else rc_min

    cbar = fig.colorbar(sm, ax=axis)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    plt.xticks(np.arange(len(f_rel.index)), labels=f_rel.index)
    plt.ylim(rc_min - 5, 100)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xlabel('Magnitude')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/dist_ev_cat_mag_recall.png')
    plt.show()


# -------------------------- Number of Stations
def plot_hist_station_distribution(df):
    plt.figure(figsize=(10, 6))

    # Contando o número de estações por evento
    sta_count = df.reset_index().groupby('Event').size()
    df['Num_Estacoes'] = df.index.get_level_values('Event').map(sta_count)

    # Histograma com frequências absolutas
    sta_count.value_counts().sort_index().plot(
        kind='bar', color='lightskyblue'
    )

    # Anotação no topo da barra com o valor da frequência
    for i, v in enumerate(sta_count.value_counts().sort_index()):
        plt.text(i, v, str(v), ha='center', va='bottom', color='black')

    plt.xticks(range(len(sta_count.unique())), sta_count.unique())
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.title('Distribuição de Eventos por Número de Estações')
    plt.xlabel('Número de Estações')
    plt.ylabel('Número de Eventos')
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/dist_ev_num_stations_absoluto.png')
    plt.show()


def plot_hist_stations_recall(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    sta_count = df.reset_index().groupby('Event').size()
    df['Num_Estacoes'] = df.index.get_level_values('Event').map(sta_count)
    rc_data = df.groupby('Num_Estacoes').apply(
        lambda x: (x['pred'] == x['label_cat']).mean() * 100
    )
    f_rel = df['Num_Estacoes'].value_counts(normalize=True)
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    bars = ax.bar(
        rc_data.index, rc_data.values,
        color=[
            sm.to_rgba(
                f_rel.get(x, 0) * 100
            ) for x in rc_data.index
        ],
        edgecolor='black',
        width=0.5,
    )
    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequência Relativa (%)')
    cbar.set_ticks([min_freq, max_freq])
    for b, l in zip(bars, rc_data.values):
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height(),
            f'{l:.2f}%',
            ha='center',
            va='bottom',
            color='black'
        )
    plt.title('Recall por Número de Estações')
    plt.xlabel('Número de Estações')
    plt.ylabel('Recall (%)')
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xticks(rc_data.index, labels=[str(int(x)) for x in rc_data.index])
    plt.ylim(60, 100)
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/dist_ev_num_stations_recall.png')
    plt.show()


# --------------------------- SNR Histograms
def snr_p(picks: pd.DataFrame,
          window: int) -> [pd.DataFrame, dict]:
    picks.sort_index(inplace=True)
    for index, pick in tqdm(picks.iterrows()):
        nw = str(obspy.UTCDateTime(pick['Pick Time']) - 9) + '/8'
        pw = str(obspy.UTCDateTime(pick['Pick Time'])) + '/' + str(window)
        sw = str(obspy.UTCDateTime(pick['Pick Time']) + 20) + '/5'
        noisewindow = parsewindow(nw)
        pwindow = parsewindow(pw)
        swindow = parsewindow(sw)
        st = obspy.read(pick['Path'])
        trace = st[0]

        filtros = filterCombos(1., 49., 4., 49.)
        dict_filt = {f'{f.pa}_{f.pb}': f for f in filtros}
        filtro_bom = dict_filt['2.0_49.0']
        noise, trace_p, trace_s = prepare(
            trace,
            filtro_bom,
            noisewindow, pwindow, swindow)

        filtro_bom.noise = np.mean(np.abs(noise))
        filtro_bom.p = np.mean(np.abs(trace_p))
        filtro_bom.s = np.mean(np.abs(trace_s))
        filtro_bom.snrp = filtro_bom.p / filtro_bom.noise
        filtro_bom.snrs = filtro_bom.s / filtro_bom.noise
        picks.loc[index, 'SNR_P'] = filtro_bom.snrp
        picks.loc[index, 'Noise'] = filtro_bom.noise
        picks.loc[index, 'p'] = filtro_bom.p

    return picks, dict_filt


# CALCULATE MEAN SNR_P FOR EVENT
def mean_snr_event(df):
    df['Mean SNR_P'] = df.index.get_level_values('Event').map(
        df.reset_index().groupby('Event')['SNR_P'].mean()
    )
    df['Mean SNR_P_cat'] = pd.Categorical(
        df['Mean SNR_P'].apply(class_snrp),
        categories=[
            '< 1', '[1-2[', '[2-3[', '[3-4[', '[4-5[', '[5-6[', '[6-7[',
            '[7-8[', '[8-9[', '[9-10[', '[10-11[', '[11-12[', '[12-13[',
            '[13-14[', '[14-15[', '>= 15'
        ],
        ordered=True
    )
    return df


def mean_mag_event(df):
    df['Mean Mag'] = df.index.get_level_values('Event').map(
        df.reset_index().groupby('Event')['MLv'].mean()
    )
    df['Mean Mag_cat'] = pd.Categorical(
        df['Mean Mag'].apply(class_mag),
        categories=['<1', '[1-2[', '[2-3[', '>=3'],
        ordered=True
    )
    return df


def mean_dist_event(df):
    df['Mean Distance'] = df.index.get_level_values('Event').map(
        df.reset_index().groupby('Event')['Distance'].mean()
    )
    df['Mean Distance_cat'] = pd.Categorical(
        df['Mean Distance'].apply(class_dist),
        categories=[
            '<50', '[50-100[', '[100-150[', '[150-200[', '[200-250[',
            '[250-300[', '>=300'
        ],
        ordered=True
    )
    return df


def class_snrp(snr):
    if snr < 1:
        return '< 1'
    elif 1 <= snr < 2:
        return '[1-2['
    elif 2 <= snr < 3:
        return '[2-3['
    elif 3 <= snr < 4:
        return '[3-4['
    elif 4 <= snr < 5:
        return '[4-5['
    elif 5 <= snr < 6:
        return '[5-6['
    elif 6 <= snr < 7:
        return '[6-7['
    elif 7 <= snr < 8:
        return '[7-8['
    elif 8 <= snr < 9:
        return '[8-9['
    elif 9 <= snr < 10:
        return '[9-10['
    elif 10 <= snr < 11:
        return '[10-11['
    elif 11 <= snr < 12:
        return '[11-12['
    elif 12 <= snr < 13:
        return '[12-13['
    elif 13 <= snr < 14:
        return '[13-14['
    elif 14 <= snr < 15:
        return '[14-15['
    else:
        return '>= 15'


# HISTOGRAM SNR FOR PICK
def plot_hist_snrs_distribution(df):
    plt.figure(figsize=(10, 6))
    # Remove the first and last values to avoid outliers
    df = df[(df['SNR_P'] > 0) & (df['SNR_P'] < 15)]
    df['SNR_P'].plot(kind='box', color='lightskyblue')
    plt.title('Distribuição de SNR_P')
    plt.xlabel('SNR_P')
    plt.ylabel('Frequência')
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/dist_snrs.png')
    plt.show()


def plot_hist_snr_recall_pick(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    cat = [
        '< 1', '[1-2[', '[2-3[', '[3-4[', '[4-5[', '[5-6[', '[6-7[', '[7-8[',
        '[8-9[', '[9-10[', '[10-11[', '[11-12[', '[12-13[', '[13-14[',
        '[14-15[', '>= 15'
    ]
    df['SNR_P_cat'] = pd.Categorical(
        df['SNR_P_cat'], categories=cat, ordered=True
    )
    f_rel = df['SNR_P_cat'].value_counts(normalize=True).sort_index()
    f_abs = df['SNR_P_cat'].value_counts().sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    rc_min = 90
    total = 0
    for c, b in zip(f_rel.index, f_abs.index):
        f_a = f_abs.loc[b]
        freq = f_rel.loc[c] * 100
        color = sm.to_rgba(freq)
        if f_a > 0:
            total += f_a
            df_c = df[df['SNR_P_cat'] == c]
            TP = df_c[(df_c['pred'] == 0) & (df_c['label_cat'] == 0)].shape[0]
            FN = df_c[(df_c['pred'] == 1) & (df_c['label_cat'] == 0)].shape[0]
            rc = 100 * TP / (TP + FN) if TP + FN != 0 else 0
            ax.bar(c, rc, color=color, edgecolor='black', width=0.5)
            ax.text(c, rc + 0.01, f'{rc:.2f}%', ha='center', va='bottom')
            ax.text(b, rc + 1.5, f'{f_a}', ha='center', va='bottom')
            rc_min = rc if rc < rc_min else rc_min
        else:
            ax.bar(c, 0, color=sm.to_rgba(0), edgecolor='black', width=0.5)
            ax.text(c, 0 + 0.01, '0.00%', ha='center', va='bottom')
            ax.text(b, 0 + 1.5, '0', ha='center', va='bottom')

    cbar = fig.colorbar(sm, ax=ax)
    plt.title(f'Recall por SNR_P Pick - Total de Eventos: {total}')
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    plt.ylim(rc_min - 5, 110)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xlabel('SNR_P')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/dist_snrs_recall.png')
    plt.show()


# HISTOGRAM  MEAN SNR FOR EVENT
def plot_mean_snr_recall_event(df):
    df_ = df.groupby(level='Event').first()
    fig, ax = plt.subplots(figsize=(10, 6))
    f_rel = df_['Mean SNR_P_cat'].value_counts(normalize=True).sort_index()
    f_abs = df_['Mean SNR_P_cat'].value_counts().sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    rc_min = 90
    total = 0
    for r, a in zip(f_rel.index, f_abs.index):
        f_a = f_abs.loc[a]
        freq = f_rel.loc[r] * 100
        mean_dist = df_[df_['Mean SNR_P_cat'] == r]['Mean Distance'].mean()
        mean_mag = df_[df_['Mean SNR_P_cat'] == r]['Mean Mag'].mean()
        nb_sta = df[df['Mean SNR_P_cat'] == r].shape[0]/f_a
        color = sm.to_rgba(freq)
        if f_a > 0:
            total += f_a
            df_c = df_[df_['Mean SNR_P_cat'] == r]
            TP = df_c[(df_c['pred'] == 0) & (df_c['label_cat'] == 0)].shape[0]
            FN = df_c[(df_c['pred'] == 1) & (df_c['label_cat'] == 0)].shape[0]
            rc = 100 * TP / (TP + FN) if TP + FN != 0 else 0
            # Reduce font size of ax.text
            ax.bar(r, rc, color=color, edgecolor='black', width=0.5)
            ax.text(
                r, rc + 0.01, f'{rc:.2f}%',
                ha='center', va='bottom', fontsize=8, fontweight='bold'
            )
            ax.text(
                a, rc + 1.5,
                f'#Freq.: {f_a}', ha='center', va='bottom',
                fontsize=8
            )
            ax.text(
                a, rc + 2.5,
                f'#Est.: {nb_sta:.1f}', ha='center', va='bottom', fontsize=8
            )
            ax.text(
                a, rc + 3.5,
                f'Dist.: {mean_dist:.0f}km', ha='center', va='bottom', fontsize=8
            )
            ax.text(
                a, rc + 4.5,
                f'Mag.: {mean_mag:.1f}', ha='center', va='bottom', fontsize=8
            )
            rc_min = rc if rc < rc_min else rc_min
        else:
            ax.bar(r, 0, color=sm.to_rgba(0), edgecolor='black', width=0.5)
            ax.text(r, 0 + 0.01, '0.00%', ha='center', va='bottom')
            ax.text(a, 0 + 1.5, '0', ha='center', va='bottom')

    cbar = fig.colorbar(sm, ax=ax)
    plt.title(f'Recall por Média de SNR_P por Evento - Total {df.shape[0]}')
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    plt.ylim(rc_min - 5, 105)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xlabel('Média de SNR_P')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('files/figures/pos_process/dist_mean_snrs_recall.png')
    plt.show()


# --------------------------- Region
def class_region(df):
    regions = gpd.read_file('files/figures/maps/macrorregioesBrasil.json')
    regions = regions.to_crs(epsg=4326)
    coord_origem = gpd.GeoDataFrame(
        df,
        geometry=[Point(x, y) for x, y in zip(
            df['Origem Longitude'], df['Origem Latitude']
        )],
        crs='EPSG:4326'
    )
    region_origem = gpd.sjoin(coord_origem, regions, how='left', op='within')
    df['Região Origem'] = region_origem['nome'].values

    return df


def plot_region_correlation(df):
    df = df.reset_index()
    df = class_region(df)
    df = df[df['Região Origem'].notna()]
    freq_orig = df['Região Origem'].value_counts(normalize=True)
    order_orig = freq_orig.index.tolist()
    cmap = plt.get_cmap('magma')
    norm_orig = mcolors.Normalize(vmin=freq_orig.min(), vmax=freq_orig.max())
    orig_colors = {
        region: cmap(norm_orig(freq)) for region, freq in freq_orig.items()
    }
    plt.figure(figsize=(18, 6))
    plt.suptitle('Correlação entre Coordenada e Probabilidade de ser Natural')
    sns.boxplot(
        x='Região Origem', y='prob_nat', data=df,
        palette=orig_colors, showfliers=False, order=order_orig,
        medianprops={'color': 'yellow'}, whiskerprops={'color': 'black'},
        meanline=True, showmeans=True, meanprops={'color': 'yellow'}
    )
    sns.stripplot(
        x='Região Origem', y='prob_nat', data=df, color='red',
        size=1.5, jitter=True, alpha=0.5, order=order_orig
    )
    plt.title(
        'Coordenada de Origem'
    )
    sm = ScalarMappable(cmap=cmap, norm=norm_orig)
    sm.set_array([])
    cax = plt.axes([0.92, 0.1, 0.02, 0.8])
    cbar = plt.colorbar(sm, orientation='vertical', cax=cax)
    cbar.set_label('Frequência Relativa')
    cbar.set_ticks([
        freq_orig.min(),
        freq_orig.max()
    ])
    cbar.set_ticklabels([
        f'{freq_orig.min() * 100:.0f}%',
        f'{freq_orig.max() * 100:.0f}%'
    ])
    plt.savefig('files/figures/pos_process/region_corr.png')
    plt.show()


# --------------------------- Create files
def load_data():
    evs = pd.read_csv('files/events/events.csv')
    evs['file_name'] = evs['Path'].apply(
        lambda x: x.split('/')[-1].split('.')[0]
    )
    df_nc_val = pd.read_csv(
        'files/output/no_commercial/validation_station_level.csv'
    )
    df_nc = pd.merge(df_nc_val, evs, on='file_name', how='left')
    df_nc.set_index(['Event', 'Station'], inplace=True)
    picks, dict_filt = snr_p(df_nc, 5)
    df_nc = class_region(df_nc)
    df_nc = mean_snr_event(df_nc)
    df_nc = mean_mag_event(df_nc)
    df_nc = mean_dist_event(df_nc)

    # df_nc.loc[:, 'prob_nat_cat'] = df_nc['prob_nat'].apply(class_prob)
    # df_nc.loc[:, 'Distance_cat'] = df_nc['Distance'].apply(class_dist)
    df_nc.loc[:, 'Magnitude_cat'] = df_nc['MLv'].apply(class_mag)
    df_nc.loc[:, 'SNR_P_cat'] = df_nc['SNR_P'].apply(class_snrp)
    df_nc.loc[:, 'Mean SNR_P_cat'] = df_nc['Mean SNR_P'].apply(class_snrp)

    # df_nc['Hora'] = df_nc['Origin Time'].apply(lambda x: UTCDateTime(x).hour)
    df_nc['Coord Origem'] = df_nc[
        ['Origem Latitude', 'Origem Longitude']
    ].apply(lambda x: [x['Origem Latitude'], x['Origem Longitude']], axis=1)

    # df_nc.to_csv('files/output/no_commercial/df_nc_pos.csv', index=True)

    return df_nc, evs


def non_commercial(df):
    # plot_hist_hour_distribution(df)
    # plot_hist_hour_recall(df)
    # ----------------------------------
    # plot_hist_station_distribution(df)
    # plot_hist_stations_recall(df)
    # ----------------------------------
    # plot_hist_distance_distribution(df)
    # plot_hist_distance_recall(df)
    # ----------------------------------
    # plot_hist_magnitude_distribution(df)
    # plot_hist_magnitude_recall(df)
    # ----------------------------------
    # plot_hist_snrs_distribution(df)
    # plot_hist_snr_recall_pick(df)
    plot_mean_snr_recall_event(df)
    # ----------------------------------
    # plot_box_dist(df)
    # plot_box_by_network(df)
    # plot_box_by_station(df)
    # plot_region_correlation(df)

    return


# -------------------------------- Main ------------------------------------- #
def main():
    df, evs = load_data()

    non_commercial(df)
    # commercial(df_c)

    return df, evs


if __name__ == '__main__':
    df, evs = main()
