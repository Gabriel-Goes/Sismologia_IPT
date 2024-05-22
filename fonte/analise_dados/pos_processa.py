# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/fonte/analise_dados/pos_processa.py

# ----------------------------  DESCRIPTION  ----------------------------------
# Script para gerar catálogo de eventos sísmicos
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.4
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
from obspy.core import AttribDict
from obspy import UTCDateTime

from shapely.geometry import Point
import geopandas as gpd

from tqdm import tqdm
from analise_dados.testa_filtros import parsewindow, prepare

from nucleo.utils import CAT_DIS, CAT_MAG, CAT_SNR

plt.dpi = 300


# --------------------------- FUNCTIONS ---------------------------------- #
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
    plt.savefig('arquivos/figuras/pos_processo/boxplot_dist.png')
    plt.show()


def plot_box_by_network(df):
    df = df.reset_index()
    stations = df['Network'].unique()
    freq_rel = df['Network'].value_counts(normalize=True)
    norm = plt.Normalize(freq_rel.min(), freq_rel.max())
    cmap = sns.cubehelix_palette(dark=.25, light=.75, start=.5, rot=-.75, as_cmap=True)
    station_colors = {station: cmap(norm(freq_rel[station])) for station in stations}

    plt.figure(figsize=(27, 9))
    ax = plt.gca()
    sns.boxplot(x='Network', y='Pick Prob_Nat', data=df, palette=station_colors, showfliers=False, ax=ax)
    sns.stripplot(x='Network', y='Pick Prob_Nat', data=df, color='black', size=1, jitter=True, alpha=0.5, ax=ax)

    ax.set_title('Boxplot da Probabilidade Natural por Rede')
    ax.set_xlabel('Rede')
    ax.set_ylabel('Probabilidade Natural')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical')
    cbar.set_label(f'Frequência Relativa - Total de Eventos: {df.shape[0]}')
    cbar.set_ticks([freq_rel.min(), freq_rel.max()])
    cbar.set_ticklabels([f'{freq_rel.min():.2f}', f'{freq_rel.max():.2f}'])

    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_process/boxplot_rede.png')
    plt.show()


def plot_box_by_station(df):
    df = df.reset_index()
    cmap = sns.cubehelix_palette(
        dark=.25, light=.75, start=.5, rot=-.75, as_cmap=True
    )
    networks = df['Network'].unique()
    for network in networks:
        network_data = df[df['Network'] == network]
        freq_rel = network_data['Station'].value_counts(normalize=True)
        norm = plt.Normalize(freq_rel.min(), freq_rel.max())
        station_colors = {station: cmap(norm(freq_rel[station])) for station in network_data['Station'].unique()}
        plt.figure(figsize=(10, 6))
        ax = sns.boxplot(x='Station', y='Pick Prob_Nat', data=network_data, palette=station_colors, showfliers=False)
        sns.stripplot(x='Station', y='Pick Prob_Nat', data=network_data, color='red', jitter=True, size=1.5, alpha=0.5, ax=ax)
        ax.set_title(f'Probabilidade Natural por Estação para a Rede {network}')
        ax.set_xlabel('Estação')
        ax.set_ylabel('Probabilidade Natural')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, orientation='vertical', ax=ax)
        cbar.set_label(f'Frequência Relativa (Total: {network_data.shape[0]})')
        ticks = np.linspace(0, 1, num=5)
        cbar.set_ticks(ticks)
        cbar.set_ticklabels([f'{norm(t) * 100:.0f}%' for t in ticks])
        plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
        plt.tight_layout()
        plt.savefig(f'arquivos/figuras/pos_process/boxplot_{network}.png')
        plt.show()


def plot_corr_matrix(df):
    cols = [
        'Event Prob_Nat', 'Pick Prob_Nat',
        'Hora',
        'Origem Latitude', 'Origem Longitude',
        'MLv', 'Distance', 'SNR_P', 'Noise'
    ]
    df = df[cols]
    plt.figure(figsize=(10, 6))
    corr = df.corr()
    sns.heatmap(
        corr, cmap='RdBu', annot=True, fmt='.2f',
        square=True, center=0, linewidths=0.5, linecolor='black'
    )
    plt.title('Correlation Matrix')
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_process/corr_matrix.png')
    plt.show()


def corr_matrix_2(df):
    relevant_columns = [
        'Distance', 'Origem Latitude', 'Origem Longitude',
        'Depth/km', 'MLv', 'Pick Prob_Nat',
        'Event Prob_Nat', 'SNR_P', 'SNR_S', 'Noise', 'p',
        'Mean SNR_P', 'Mean Distance', 'Hora'
    ]

    df_corr = df[relevant_columns].dropna()
    corr_m = df_corr.corr()
    plt.figure(figsize=(14, 10))
    sns.heatmap(
        corr_m, annot=True, fmt=".2f", cmap='coolwarm', center=0,
        square=True, linewidths=0.5, linecolor='black'
    )
    plt.title('Matriz de Correlação')
    plt.show()

    pick_prob_nat_corr = corr_m['Pick Prob_Nat'].sort_values(ascending=False)
    event_prob_nat_corr = corr_m['Event Prob_Nat'].sort_values(ascending=False)
    print(pick_prob_nat_corr)
    print(event_prob_nat_corr)


# --------------------------- PROBABILITIES
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
    plt.savefig('arquivos/figuras/pos_processo/dist_prob_nat.png')
    plt.show()


def plot_mean_snr_prob_nat(df, n=1):
    df = df[df['SNR_P'] > n]
    df = df[df['Distance'] < n]
    df.set_index(['Event', 'Station'], inplace=True)
    df = mean_snr_event(df)
    df['Mean SNR_P_cat'] = pd.Categorical(
        df['Mean SNR_P_cat'], categories=CAT_SNR, ordered=True
    )
    df.loc[:, 'SNR_P_cat'] = df['SNR_P'].apply(class_snrp)
    df.loc[:, 'Mean SNR_P_cat'] = df['Mean SNR_P'].apply(class_snrp)
    df_ = df.groupby(level='Event').first()
    df_.sort_values('Mean SNR_P', inplace=True)
    f_rel = df_['Mean SNR_P_cat'].value_counts(normalize=True).sort_index()
    f_abs = df_['Mean SNR_P_cat'].value_counts().sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    prob_min = 90
    total = 0
    fig, ax = plt.subplots(figsize=(21, 9))
    for r, a in zip(f_rel.index, f_abs.index):
        f_a = f_abs.loc[a]
        freq = f_rel.loc[r] * 100
        mean_dist = df_[df_['Mean SNR_P_cat'] == r]['Mean Distance'].mean()
        nb_sta = df[df['Mean SNR_P_cat'] == r].shape[0]/f_a
        color = sm.to_rgba(freq)
        if f_a > 0:
            total += f_a
            df_c = df_[df_['Mean SNR_P_cat'] == r]
            prob = (df_c['prob_nat'].mean() * 100)
            ax.bar(r, prob, color=color, edgecolor='black', width=0.5)
            ax.text(
                r, prob + 0.01, f'{prob:.2f}%',
                ha='center', va='bottom', fontsize=8, fontweight='bold'
            )
            ax.text(
                a, prob + 1.5,
                f'#Freq.: {f_a}', ha='center', va='bottom',
                fontsize=8
            )
            ax.text(
                a, prob + 2.5, f'#Est.: {nb_sta:.1f}',
                ha='center', va='bottom', fontsize=8
            )
            ax.text(
                a, prob + 3.5, f'Dist.: {mean_dist:.0f}km',
                ha='center', va='bottom', fontsize=8
            )
            prob_min = prob if prob < prob_min else prob_min
        else:
            ax.bar(r, 0, color=sm.to_rgba(0), edgecolor='black', width=0.5)
            ax.text(r, 0 + 0.01, '0.00%', ha='center', va='bottom')
            ax.text(a, 0 + 1.5, '0', ha='center', va='bottom')

    cbar = fig.colorbar(sm, ax=ax)
    plt.title(
        f'Probabilidade por Média de SNR_P ({n}) por Evento -\
        Total {df_.shape[0]}'
    )
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    plt.ylim(prob_min - 5, 100)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xlabel('Média de SNR_P')
    plt.ylabel('Probabilidade Natural(%)')
    plt.tight_layout()
    plt.savefig(
        f'arquivos/figuras/pos_processo/mean_snrs_{n}_prob_nat.png'
    )
    # Set dpi
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
    plt.savefig('arquivos/figuras/pos_processo/dist_prob_nat_recall.png')
    plt.show()


# --------------------------- HOURS
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
    plt.savefig(
        'arquivos/figuras/pos_processo/hist_hora.png'
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
    plt.savefig('arquivos/figuras/pos_processo/hist_ev_hour_recall.png')
    plt.show()
    plt.close()


# --------------------------- DISTANCES
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
    plt.savefig('arquivos/figuras/pos_processo/dist_ev_distance_rel_freq.png')
    plt.show()


def plot_hist_distance_recall(df):
    df['Distance_cat'] = pd.Categorical(
        df['Distance_cat'], categories=CAT_DIS, ordered=True
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
    plt.savefig('arquivos/figuras/pos_processo/hist_ev_distance.png')
    plt.show()
    plt.close()


# --------------------------- MAGNITUDES
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
        ordered=True
    )
    df['Magnitude_cat'].value_counts().sort_index().plot(
        kind='bar', color='lightskyblue'
    )
    plt.title('Distribuição de Eventos por Categoria de Magnitude')
    plt.xlabel('Categoria de Magnitude')
    plt.ylabel('Número de Eventos')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_processo/dist_ev_cat_mag.png')
    plt.show()


def plot_hist_magnitude_recall(df):
    fig, axis = plt.subplots(figsize=(10, 6))
    df['Magnitude_cat'] = pd.Categorical(
        df['Magnitude_cat'], categories=CAT_MAG, ordered=True
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
    plt.savefig('arquivos/figuras/pos_processo/dist_ev_cat_mag_recall.png')
    plt.show()


# --------------------------- NUMBER OF STATIONS
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
    plt.savefig(
        'arquivos/figuras/pos_processo/dist_ev_num_stations_absoluto.png'
    )
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
    plt.savefig(
        'arquivos/figuras/pos_processo/dist_ev_num_stations_recall.png'
    )
    plt.show()


# --------------------------- SNR HISTOGRAMS
def snr(eventos: pd.DataFrame,
        window: int) -> [pd.DataFrame, dict]:
    eventos.sort_index(inplace=True)
    filtro = AttribDict({
        'pa': 2.0, 'pb': 49.0,
        'noise': '', 'p': '', 's': '', 'snrp': '', 'snrs': ''
    })
    for index, pick in tqdm(eventos.iterrows()):
        nw = str(obspy.UTCDateTime(pick['Pick Time']) - 4.9) + '/4'
        pw = str(obspy.UTCDateTime(pick['Pick Time'])) + '/' + str(window)
        sw = str(obspy.UTCDateTime(pick['Pick Time']) + 20) + '/5'
        noisewindow = parsewindow(nw)
        pwindow = parsewindow(pw)
        swindow = parsewindow(sw)
        st = obspy.read(pick['Path'])
        noise, trace_p, trace_s = prepare(
            st[0],
            filtro,
            noisewindow, pwindow, swindow
        )
        filtro.noise = np.mean(np.abs(noise))
        filtro.p = np.mean(np.abs(trace_p))
        filtro.s = np.mean(np.abs(trace_s))
        filtro.snrp = filtro.p / filtro.noise
        filtro.snrs = filtro.s / filtro.noise
        eventos.loc[index, 'SNR_P'] = filtro.snrp
        eventos.loc[index, 'SNR_S'] = filtro.snrs
        eventos.loc[index, 'Noise'] = filtro.noise
        eventos.loc[index, 'p'] = filtro.p

    return eventos


def mean_snr_event(df):
    df['Mean SNR_P'] = df.index.get_level_values('Event').map(
        df.reset_index().groupby('Event')['SNR_P'].mean()
    )
    df['Mean SNR_P_cat'] = pd.Categorical(
        df['Mean SNR_P'].apply(class_snrp),
        categories=CAT_SNR,
        ordered=True
    )
    return df


def mean_dist_event(df):
    df['Mean Distance'] = df.index.get_level_values('Event').map(
        df.reset_index().groupby('Event')['Distance'].mean()
    )
    df['Mean Distance_cat'] = pd.Categorical(
        df['Mean Distance'].apply(class_dist),
        categories=CAT_DIS,
        ordered=True
    )
    return df


def class_snrp(snr):
    if snr < 1:
        return '< 1'
    else:
        snr_c = 1
        while snr_c < 15:
            if snr_c <= snr < snr_c + 1:
                return f'[{snr_c}-{snr_c + 1}['
            snr_c += 1
        return '>= 15'


def plot_hist_snrs_distribution(df):
    plt.figure(figsize=(10, 6))
    df = df[(df['SNR_P'] > 0) & (df['SNR_P'] < 15)]
    df['SNR_P'].plot(kind='box', color='lightskyblue')
    plt.title('Distribuição de SNR_P')
    plt.xlabel('SNR_P')
    plt.ylabel('Frequência')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_processo/dist_snrs.png')
    plt.show()


def plot_hist_snr_recall_pick(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    df['SNR_P_cat'] = pd.Categorical(
        df['SNR_P_cat'], categories=CAT_SNR, ordered=True
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
    plt.title(f'Recall por SNR_P Pick - Total de Picks: {total}')
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    plt.ylim(rc_min - 5, 110)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xlabel('SNR_P')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_processo/dist_snrs_recall.png')
    plt.show()


def scatter_snr_prob(df):
    df['SNR_P_log'] = np.log10(df['SNR_P'])
    # df['SNR_S_log'] = np.log10(df['SNR_S'])
    plt.figure(figsize=(10, 6))
    # supperposition of the scatter plot
    plt.scatter(df['SNR_P_log'], df['prob_nat'], alpha=0.5)
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.title('Scatter Plot SNR_P x Probabilidade Natural')
    plt.xlabel('SNR_P_log')
    plt.ylabel('Probabilidade Natural')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_processo/scatter_snrs_prob_nat.png')
    plt.show()


def recall_event(df):
    plt.figure(figsize=(10, 6))
    n = 1
    while n < 15:
        df = df[df['SNR_P'] > n]
        df = mean_snr_event(df)
        df['Mean SNR_P_cat'] = pd.Categorical(
            df['Mean SNR_P_cat'], categories=CAT_SNR, ordered=True
        )
        df.loc[:, 'SNR_P_cat'] = df['SNR_P'].apply(class_snrp)
        df.loc[:, 'Mean SNR_P_cat'] = df['Mean SNR_P'].apply(class_snrp)

        # by event, sum the pred_nat value and divide by the number of stations
        Events_pred = df.groupby(level='Event').apply(
            lambda x: x['prob_nat'].sum() / x.shape[0]
        )
        # if Events_pred > 0.5, then the event is classified as natural
        Events_pred = Events_pred.apply(lambda x: 0 if x > 0.5 else 1)
        # get the label of the event
        Events_label = df.groupby(level='Event').first()['label_cat']

        def recall_score(y_true, y_pred):
            return np.mean(y_true == y_pred)
        rec_score = recall_score(Events_label, Events_pred)
        plt.plot(n, rec_score, 'ro')
        n += 1
    plt.title('Recall por Evento')
    plt.xlabel('SNR_P')
    plt.ylabel('Recall')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_processo/recall_event.png')
    plt.show()


# --------------------------- REGION
def class_region(df):
    regions = gpd.read_file('arquivos/figuras/mapas/macrorregioesBrasil.json')
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
    plt.savefig('arquivos/figuras/pos_processo/region_corr.png')
    plt.show()


# --------------------------- CREATE ARQUIVOS
def carregar_dado(tipo='ncomercial', n=0, mlv=4):
    df = pd.read_csv('arquivos/resultados/predito.csv')
    df = df[df['MLv'] <= mlv]
    df.set_index(['Event', 'Station'], inplace=True)
    df = snr(df, 3)
    df = df[df['SNR_P'] > n]
    df = class_region(df)
    df = mean_snr_event(df)
    df = mean_dist_event(df)
    df.loc[:, 'prob_nat_cat'] = df['Pick Prob_Nat'].apply(class_prob)
    df.loc[:, 'Distance_cat'] = df['Distance'].apply(class_dist)
    df.loc[:, 'Magnitude_cat'] = df['MLv'].apply(class_mag)
    df.loc[:, 'SNR_P_cat'] = df['SNR_P'].apply(class_snrp)
    df.loc[:, 'Mean SNR_P_cat'] = df['Mean SNR_P'].apply(class_snrp)

    df['Hora'] = df['Origin Time'].apply(lambda x: UTCDateTime(x).hour)
    df['Coord Origem'] = df[
        ['Origem Latitude', 'Origem Longitude']
    ].apply(lambda x: [x['Origem Latitude'], x['Origem Longitude']], axis=1)

    df.to_csv('arquivos/resultados/analisado.csv')
    return df


def ncomercial(df):
    # plot_hist_hour_distribution(df)
    # plot_hist_hour_recall(df)
    # ----------------------------------
    # plot_hist_station_distribution(df)
    plot_hist_stations_recall(df)
    # ----------------------------------
    # plot_hist_distance_distribution(df)
    plot_hist_distance_recall(df)
    # ----------------------------------
    # plot_hist_magnitude_distribution(df)
    plot_hist_magnitude_recall(df)
    # ----------------------------------
    plot_hist_snrs_distribution(df)
    plot_hist_snr_recall_pick(df)
    # plot_mean_snr_recall_event(df)
    # ----------------------------------
    plot_box_dist(df)
    # plot_box_by_network(df)
    # plot_box_by_station(df)
    plot_region_correlation(df)

    return


# -------------------------------- MAIN ------------------------------------- #
def main():
    df = carregar_dado()
    ncomercial(df)
    # comercial(df_c)

    return df


if __name__ == '__main__':
    df, evs = main()
