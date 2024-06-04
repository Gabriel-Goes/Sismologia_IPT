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

from nucleo.utils import CAT_DIS, CAT_MAG, CAT_SNR, CAT_PROB


# --------------------------- FUNCTIONS ---------------------------------- #
def plot_box_dist(df, df_2):
    fig, axes = plt.subplots(3, 5, figsize=(9, 21))
    df = df.groupby(['Event']).first()
    sns.histplot(
        df[df['Event Pred_final'] == 'Natural']['Event Prob_Nat'],
        bins=20, kde=True, ax=axes[0, 0], color='blue'
    )
    axes[0, 0].set_title('Distribuição de prob_nat para Eventos Naturais',
                         fontsize=7)
    sns.histplot(
        df[df['Event Pred_final'] == 'Anthropogenic']['Event Prob_Nat'],
        bins=20, kde=True, ax=axes[0, 0], color='red'
    )
    sns.boxplot(x='Event Pred_final', y='Distance_Q2', data=df, ax=axes[0, 2])
    sns.boxplot(x='Event Pred_final', y='MLv', data=df, ax=axes[0, 3])
    sns.boxplot(x='Event Pred_final', y='Hora', data=df_2, ax=axes[0, 4])
    sns.boxplot(x='Event Pred_final', y='SNR_P_Q2', data=df, ax=axes[0, 1],
                showfliers=False)

    sns.boxplot(x='Região Origem', y='Event Prob_Nat', data=df, ax=axes[2, 0])
    sns.boxplot(x='Num_Estacoes', y='Distance_Q2', data=df, ax=axes[1, 0])
    sns.boxplot(x='Num_Estacoes', y='Event Prob_Nat', data=df, ax=axes[1, 1],
                showfliers=False)
    df_1 = df[df['Num_Estacoes'] > 1]
    sns.boxplot(x='Num_Estacoes', y='SNR_P_Q2', data=df_1, ax=axes[1, 2],
                showfliers=False)
    sns.boxplot(x='Região Origem', y='Event Prob_Nat', data=df, ax=axes[2, 0])

    plt.savefig('arquivos/figuras/pos_process/boxplot_dist.png', dpi=300)
    plt.tight_layout()
    #plt.show()()


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
    #plt.show()()


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
        #plt.show()()


def plot_corr_matrix(df):
    df_ = df.groupby(level='Event').first()
    cols = [
        'Event Prob_Nat',
        'Hora',
        'Origem Latitude', 'Origem Longitude',
        'SNR_P_Q2', 'SNR_P', 'Noise',
        'Depth/km', 'MLv',
        'Distance_Q2', 'Distance',
        'Num_Estacoes'
    ]
    df_ = df_[cols]
    plt.figure(figsize=(10, 6))
    corr = df_.corr()
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
    #plt.show()()

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
    plt.savefig('arquivos/figuras/pos_process/dist_prob_nat.png')
    #plt.show()()


def hist_median_snr_prob_nat(df, n=0, d=400, m=8):
    df = df[df['SNR_P'] > n]
    df = df[df['Distance'] < 200]
    df = df[df['MLv'] < m]
    df = median_snrp_event(df)
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
            prob = (df_c['Event Prob_Nat'].mean() * 100)
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
        f'arquivos/figuras/pos_process/mean_snrs_{n}_prob_nat.png'
    )
    # Set dpi
    #plt.show()()


def plot_hist_prob_recall(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    df['prob_nat_cat'] = pd.Categorical(
        df['prob_nat_cat'], categories=CAT_PROB, ordered=True
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
        TP = df_c[(df_c['pred'] == 0) & (df_c['Label'] == 0)].shape[0]
        FN = df_c[(df_c['pred'] == 1) & (df_c['Label'] == 0)].shape[0]
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
    plt.savefig('arquivos/figuras/pos_process/dist_prob_nat_recall.png')
    #plt.show()()


# --------------------------- HOURS
def hist_hour_distribution(df):
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
    plt.title(f'Distribuição de eventos sísmicos por hora (UTC) - Total {df.shape[0]}')
    plt.xlabel('Hora (UTC)')
    plt.ylabel('Frequência')
    # Legenda: Commercial e Não-Comercial
    plt.legend(['Não-Comercial'], loc='upper right')
    plt.savefig(
        'arquivos/figuras/pos_process/hist_hora.png'
    )
    #plt.show()()


def hist_hour_recall_pick(df):
    df['Hora'] = pd.to_numeric(df['Hora'])
    df['Cat Hora'] = pd.cut(
        df['Hora'], bins=range(0, 25, 1), right=False, labels=range(0, 24, 1)
    )
    f_rel = df['Cat Hora'].value_counts(normalize=True).sort_index()
    f_abs = df['Cat Hora'].value_counts().sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel[f_rel > 0].min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    cmap = plt.cm.magma
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    y_min = 90
    y_max = 0

    fig, ax = plt.subplots(figsize=(24, 8))
    for h in f_rel.index:
        h_df = df[df['Cat Hora'] == h]
        TP = h_df[(h_df['Pick Pred'] == 0) & (h_df['Label'] == 0)].shape[0]
        FN = h_df[(h_df['Pick Pred'] == 1) & (h_df['Label'] == 0)].shape[0]
        if TP + FN == 0:
            rc = 0
        else:
            rc = TP / (TP + FN) * 100
        if rc != 0:
            y_min = rc if rc < y_min else y_min
            y_max = rc if rc > y_max else y_max
            freq = f_rel.loc[h] * 100
            cor = cmap(norm(freq))
            ax.bar(
                h, rc, color=cor, edgecolor='black', width=0.5, align='center'
            )
            ax.text(
                h, rc + 0.5, f'{rc:.0f}%', fontsize=8,
                ha='center', va='bottom', color='black'
            )
            ax.text(
                h, rc + 1.5, f'{f_abs.loc[h]}', fontsize=8,
                ha='center', va='bottom', color='black'
            )
    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    cbar.set_ticklabels([f'{min_freq:.2f}%', f'{max_freq:.2f}%'])
    plt.xticks(range(0, 24, 1), labels=[f'{h}h' for h in range(0, 24, 1)])
    plt.ylim(y_min - 5, y_max + 5)
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray', axis='y')
    plt.title(f'Distribuição de Recall por Hora dos Eventos - Pick Level Total: {df.shape[0]}')
    plt.xlabel('Hora do Dia')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_process/hist_ev_hour_recall_pick.png')
    #plt.show()()
    plt.close()


def hist_hour_recall_event(df):
    df['Hora'] = pd.to_numeric(df['Hora'])
    df['Cat Hora'] = pd.cut(
        df['Hora'], bins=range(0, 25, 1), right=False, labels=range(0, 24, 1)
    )
    df = df.groupby(level='Event').first()
    f_rel = df['Cat Hora'].value_counts(normalize=True).sort_index()
    f_abs = df['Cat Hora'].value_counts().sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel[f_rel > 0].min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    cmap = plt.cm.magma
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    y_min = 90

    fig, ax = plt.subplots(figsize=(14, 8))
    for h in f_rel.index:
        h_df = df[df['Cat Hora'] == h]
        TP = h_df[(h_df['Event Pred'] == 0) & (h_df['Label'] == 0)].shape[0]
        FN = h_df[(h_df['Event Pred'] == 1) & (h_df['Label'] == 0)].shape[0]
        if TP + FN == 0:
            rc = 0
        else:
            rc = TP / (TP + FN) * 100
        if rc != 0:
            y_min = rc if rc < y_min else y_min
            freq = f_rel.loc[h] * 100
            cor = cmap(norm(freq))
            ax.bar(
                h, rc, color=cor, edgecolor='black', width=0.5, align='center'
            )
            ax.text(
                h, rc + 0.5, f'{rc:.0f}%', ha='center', va='bottom', color='black',
                fontsize=8
            )
            ax.text(
                h, rc + 1.5, f'{f_abs.loc[h]}', ha='center', va='bottom',
                color='black', fontsize=8
            )

    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    cbar.set_ticklabels([f'{min_freq:.2f}%', f'{max_freq:.2f}%'])
    plt.xticks(range(0, 24, 1), labels=[f'{h}h' for h in range(0, 24, 1)])
    plt.ylim(y_min - 5, 100)
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray', axis='y')
    plt.title(f'Distribuição de Recall por Hora dos Eventos - Event Level Total: {df.shape[0]}')
    plt.xlabel('Hora do Dia')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_process/hist_ev_hour_recall_event.png')
    # #plt.show()()


# --------------------------- DISTANCES
def class_dist(dist):
    if dist < 25:
        return '< 25'
    else:
        dist_c = 25
        while dist_c < 350:
            if dist_c <= dist < dist_c + 25:
                return f'[{dist_c}-{dist_c + 25}['
            dist_c += 25
        return '>= 350'


def median_dist_event(df):
    df['Distance_Q2'] = df.index.get_level_values('Event').map(
        df.reset_index().groupby('Event')['Distance'].median()
    )
    df['Distance_Q2_cat'] = pd.Categorical(
        df['Distance_Q2'].apply(class_dist),
        categories=CAT_DIS,
        ordered=True
    )
    return df


def closest_dist_event(df):
    df.sort_values('Distance', inplace=True)
    df['Distance_n'] = df.index.get_level_values('Event').map(
        df.reset_index().groupby('Event')['Distance'].first()
    )
    df['Distance_n_cat'] = pd.Categorical(
        df['Distance_n'].apply(class_dist),
        categories=CAT_DIS,
        ordered=True
    )
    return df


def dist_event(df):
    df['Distance_cat'] = pd.Categorical(
        df['Distance'].apply(class_dist),
        categories=CAT_DIS,
        ordered=True
    )
    return df


def hist_dist_distrib(df):
    n, bins, patches = plt.hist(
        df['Distance'],
        bins=range(25, 425, 25),
        rwidth=0.8,
        color='lightskyblue',
        weights=np.zeros_like(df['Distance']) + 1. / df['Distance'].size
    )
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
    plt.savefig('arquivos/figuras/pos_process/dist_ev_distance_rel_freq.png')
    #plt.show()()


def hist_dist_recall_pick(df, n=0, d=400, m=8):
    df = df[df['SNR_P'] > n]
    df = df[df['Distance'] < d]
    df = df[df['MLv'] < m]
    f_rel = df['Distance_cat'].value_counts(normalize=True).sort_index()
    f_abs = df['Distance_cat'].value_counts().sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    fig, ax = plt.subplots(figsize=(9, 6))

    for c in f_rel.index:
        c_df = df[df['Distance_cat'] == c]
        TP = c_df[(c_df['Event Pred'].astype(int) == 0) & (c_df['Label'] == 0)].shape[0]
        FN = c_df[(c_df['Event Pred'].astype(int) == 1) & (c_df['Label'] == 0)].shape[0]
        if TP + FN == 0:
            rc = 0
        else:
            rc = TP / (TP + FN) * 100
            freq = f_rel.loc[c] * 100
            color = sm.to_rgba(freq)
            ax.bar(c, rc, color=color, edgecolor='black', width=0.5)
            ax.text(c, rc + 0.25, f'{rc:.2f}',
                    ha='center', va='bottom',
                    fontsize=6, fontweight='bold')
            ax.text(c, rc + 1, f'#{f_abs.loc[c]}',
                    ha='center', va='bottom',
                    fontsize=8)

    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, f_rel.mean() * 100, max_freq])
    plt.xticks(
        np.arange(len(f_rel.index)),
        labels=[
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
    )
    plt.ylim(50, 100)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.gca().xaxis.grid(False)
    plt.xlabel('Epicentral Distance (km)')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig(f'arquivos/figuras/pos_process/{n}{d}{m}_hist_ev_distance.png', dpi=300)
    #plt.show()()
    plt.close()


def hist_dist_recall_event(df, n=0, d=400, m=8):
    df = df[df['SNR_P'] > n]
    df = df[df['Distance'] < d]
    df = df[df['MLv'] < m]
    df.sort_values('Distance', inplace=True)
    df = df.groupby(level='Event').first()
    f_rel = df['Distance_cat'].value_counts(normalize=True).sort_index()
    f_abs = df['Distance_cat'].value_counts().sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    fig, ax = plt.subplots(figsize=(9, 6))
    rc_min = 90

    for c in f_rel.index:
        c_df = df[df['Distance_cat'] == c]
        desc_df = c_df.describe()
        TP = c_df[(c_df['Event Pred'].astype(int) == 0) & (c_df['Label'] == 0)].shape[0]
        FN = c_df[(c_df['Event Pred'].astype(int) == 1) & (c_df['Label'] == 0)].shape[0]
        if TP + FN == 0:
            rc = 0
        else:
            rc = TP / (TP + FN) * 100
            rc_min = rc if rc < rc_min else rc_min
            freq = f_rel.loc[c] * 100
            color = sm.to_rgba(freq)
            ax.bar(c, rc, color=color, edgecolor='black', width=0.25)
            ax.text(c, rc + 0.25, f'{rc:.1f}%',
                    ha='center', va='bottom',
                    fontsize=6, fontweight='bold')
            ax.text(c, rc + 1, f'#{f_abs.loc[c]}',
                    ha='center', va='bottom',
                    fontsize=6)
            ax.text(c, rc + 2, f'prob: {desc_df.loc["50%", "Pick Prob_Nat"]*100:.2f} +- {desc_df.loc["std", "Pick Prob_Nat"]*100:.2f}%',
                    ha='center', va='bottom',
                    fontsize=6)

    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, f_rel.mean() * 100, max_freq])
    plt.xticks(
        np.arange(len(f_rel.index)),
        labels=[
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
            '[325-350',
            '>= 350'
        ],
        fontsize=8,
        rotation=45
    )
    plt.suptitle('Recall por Classes de Distância Epicentral Mais Próxima')
    plt.title(f'Total de Eventos: {df.shape[0]} | SNR_P > {n} | Distância < {d} | MLv < {m}')
    plt.ylim(rc_min - 5, 103)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.gca().xaxis.grid(False)
    plt.xlabel('Nearest Pick To Epicentral Distance (km)')
    plt.ylabel('Event Recall (%)')
    plt.tight_layout()
    plt.savefig(f'arquivos/figuras/pos_process/{n}{d}{m}_hist_ev_distance_event.png')
    #plt.show()()


def box_dist_event_prob(df, n=0, d=400, m=8):
    df = df[df['SNR_P'] > n]
    df = df[df['Distance'] < d]
    df = df[df['MLv'] < m]
    df.sort_values('Distance', inplace=True)
    df_ = df.groupby(level='Event').first()
    f_rel = df_['Distance_cat'].value_counts(normalize=True).sort_index()
    palette = sns.color_palette('Paired', n_colors=(f_rel.shape[0]))
    color_map = {c: palette[i] for i, c in enumerate(f_rel.index)}
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='Paired', norm=norm)
    sm.set_array([])
    fig, ax = plt.subplots(figsize=(19, 9))
    box_data = []
    positions = np.arange(len(f_rel.index))

    for pos, c in zip(positions, f_rel.index):
        c_df = df_[df_['Distance_cat'] == c]
        prob_data = c_df['Event Prob_Nat'] * 100
        box_data.append(prob_data)
        freq = f_rel.loc[c] * 100
        color = sm.to_rgba(freq)
        bp = ax.boxplot(
            prob_data, positions=[pos], widths=0.5, patch_artist=True
        )
        for patch in bp['boxes']:
            patch.set_facecolor(color)
            patch.set_edgecolor('black')
        for whisker in bp['whiskers']:
            whisker.set_color('black')
        for cap in bp['caps']:
            cap.set_color('black')
        for median in bp['medians']:
            median.set_color('red')
            ax.text(
                pos+0.5, median.get_ydata()[0],
                f'{median.get_ydata()[0]:.2f}%',
                ha='center', va='bottom', fontsize=5
            )
        for flier in bp['fliers']:
            flier.set(marker='.', color='black', alpha=0.5)

        TP = c_df[(c_df['Event Pred'] == 0) & (c_df['Label'] == 0)].shape[0]
        FN = c_df[(c_df['Event Pred'] == 1) & (c_df['Label'] == 0)].shape[0]
        if TP + FN == 0:
            rc = 0
        else:
            rc = TP / (TP + FN) * 100
            ax.text(
                pos, 102, f'{rc:.2f}%',
                ha='center', va='bottom', fontsize=7, fontweight='bold'
            )

    plt.text(
        -0.9, 102, 'Recall ->',
        ha='center', va='bottom', fontsize=7, fontweight='bold')
    plt.xticks(
        np.arange(len(f_rel.index)),
        labels=[
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
            '[325-350',
            '>= 350'
        ],
        fontsize=8,
        rotation=45
    )
    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks(np.linspace(min_freq, max_freq, num=12))
    cbar.set_ticklabels(np.linspace(min_freq, max_freq, num=12).astype(int))
    plt.suptitle('Boxplot da Probabilidade de Evento Ser Natural por Classes de Distância Epicentral Mais Próxima')
    plt.title(
        f'Total de Eventos: {df_.shape[0]} | SNR_P > {n} | Distância < {d} | MLv < {m}',
        fontsize=7
    )
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.gca().xaxis.grid(False)
    plt.axhline(y=50, color='red', linestyle='--', linewidth=0.25)
    plt.xlabel('Nearest Pick To Epicentral Distance (km)')
    plt.ylabel('Probability of Natural Event (%)')
    plt.tight_layout()
    plt.savefig(f'arquivos/figuras/pos_process/{n}{d}{m}_boxplot_ev_distance_event.png')
    #plt.show()()


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


def hist_magnitude_distribution(df):
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
    plt.savefig('arquivos/figuras/pos_process/dist_ev_cat_mag.png')
    #plt.show()()


def hist_magnitude_recall(df, n=0, d=400, m=8):
    df = df[df['SNR_P'] > n]
    df = df[df['Distance'] < d]
    df = df[df['MLv'] < m]
    df = df.groupby(level='Event').first()
    df['Magnitude_cat'] = pd.Categorical(
        df['Magnitude_cat'], categories=CAT_MAG, ordered=True
    )
    f_rel = df['Magnitude_cat'].value_counts(normalize=True).sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=0, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    rc_min = 90
    fig, axis = plt.subplots(figsize=(10, 6))
    for c in f_rel.index:
        df_c = df[df['Magnitude_cat'] == c]
        TP = df_c[(df_c['Event Pred'] == 0) & (df_c['Label'] == 0)].shape[0]
        FN = df_c[(df_c['Event Pred'] == 1) & (df_c['Label'] == 0)].shape[0]
        rc = 100 * TP / (TP + FN) if TP + FN != 0 else 0
        freq = f_rel.loc[c] * 100
        color = sm.to_rgba(freq)
        axis.bar(c, rc, color=color, edgecolor='black', width=0.5)
        axis.text(c, rc + 0.01, f'{rc:.2f}%', ha='center', va='bottom')
        rc_min = rc if rc < rc_min else rc_min
    cbar = fig.colorbar(sm, ax=axis)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    plt.suptitle('Recall por Classes de Magnitude')
    plt.title(f'Total de Eventos: {df.shape[0]}')
    plt.xticks(np.arange(len(f_rel.index)), labels=f_rel.index)
    plt.ylim(rc_min - 5, 100)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xlabel('Magnitude')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_process/dist_ev_cat_mag_recall.png')
    # #plt.show()()


def box_mag_event_prob(df, n=0, d=400, m=8):
    df = df[df['SNR_P'] > n]
    df = df[df['Distance'] < d]
    df = df[df['MLv'] < m]
    df.sort_values('MLv', inplace=True)
    df_ = df.groupby(level='Event').first()
    df['Magnitude_cat'] = pd.Categorical(
        df['Magnitude_cat'], categories=CAT_MAG, ordered=True
    )
    f_rel = df_['Magnitude_cat'].value_counts(normalize=True).sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=norm)
    sm.set_array([])
    fig, ax = plt.subplots(figsize=(19, 9))
    box_data = []
    total_rc = 0
    positions = np.arange(len(f_rel.index))
    print(f_rel.index)
    for pos, c in zip(positions, f_rel.index):
        c_df = df_[df_['Magnitude_cat'] == c]
        prob_data = c_df['Event Prob_Nat'] * 100
        box_data.append(prob_data)
        freq = f_rel.loc[c] * 100
        color = sm.to_rgba(freq)
        bp = ax.boxplot(
            prob_data, positions=[pos], widths=0.5, patch_artist=True
        )
        for patch in bp['boxes']:
            patch.set_facecolor(color)
            patch.set_edgecolor('black')
        for whisker in bp['whiskers']:
            whisker.set_color('black')
        for cap in bp['caps']:
            cap.set_color('black')
        for median in bp['medians']:
            median.set_color('red')
            ax.text(
                pos+0.35, median.get_ydata()[0],
                f'{median.get_ydata()[0]:.2f}%',
                ha='center', va='bottom', fontsize=5
            )
        for flier in bp['fliers']:
            flier.set(marker='.', color='black', alpha=0.5)
        TP = c_df[(c_df['Event Pred'] == 0) & (c_df['Label'] == 0)].shape[0]
        FN = c_df[(c_df['Event Pred'] == 1) & (c_df['Label'] == 0)].shape[0]
        if TP + FN == 0:
            rc = 0
        else:
            rc = TP / (TP + FN) * 100
            ax.text(
                pos, 102, f'{rc:.2f}%',
                ha='center', va='bottom', fontsize=7, fontweight='bold'
            )
    plt.text(
        -0.25, 102, 'Recall ->',
        ha='center', va='bottom', fontsize=7, fontweight='bold')

    plt.xticks(
        np.arange(len(f_rel.index)),
        labels=f_rel.index,
        fontsize=8,
        rotation=45
    )
    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks(np.linspace(min_freq, max_freq, num=4))
    cbar.set_ticklabels(np.linspace(min_freq, max_freq, num=4).astype(int))
    plt.suptitle('Boxplot da Probabilidade de Evento Ser Natural por Classes de Magnitude')
    plt.title(
        f'Total de Eventos: {df_.shape[0]} | SNR_P > {n} | Distância < {d} | MLv < {m}',
        fontsize=7
    )
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.gca().xaxis.grid(False)
    plt.axhline(y=50, color='red', linestyle='--', linewidth=0.25)
    plt.xlabel('Magnitude')
    plt.ylabel('Probability of Natural Event (%)')
    plt.tight_layout()
    plt.savefig(f'arquivos/figuras/pos_process/{n}{d}{m}_boxplot_ev_mag_event.png')
    # #plt.show()()


# --------------------------- NUMBER OF STATIONS
def hist_sta_distribution(df):
    plt.figure(figsize=(10, 6))
    sta_count = df.reset_index().groupby('Event').size()
    df['Num_Estacoes'] = df.index.get_level_values('Event').map(sta_count)
    sta_count.value_counts().sort_index().plot(
        kind='bar', color='lightskyblue'
    )
    for i, v in enumerate(sta_count.value_counts().sort_index()):
        plt.text(i, v, str(v), ha='center', va='bottom', color='black')
    plt.xticks(range(len(sta_count.unique())), sorted(sta_count.unique()))
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.title('Distribuição de Eventos por Número de Estações')
    plt.xlabel('Número de Estações')
    plt.ylabel('Número de Eventos')
    plt.tight_layout()
    plt.savefig(
        'arquivos/figuras/pos_process/dist_ev_num_stations_absoluto.png'
    )
    #plt.show()()


def hist_sta_recall_pick(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    ev_count = df.reset_index().groupby('Event').size()
    df['Num_Estacoes'] = df.index.get_level_values('Event').map(ev_count)
    rc_data = df.groupby('Num_Estacoes').apply(
        lambda x: (x['Pick Pred'] == x['Label']).mean() * 100
    )
    y_min = rc_data.min() - 5
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
            b.get_x() + b.get_width() / 2, b.get_height(),
            f'{l:.2f}%', ha='center', va='bottom', color='black', fontsize=8
        )
    plt.title(f'Recall por Número de Estações - Pick Level (Total {df.shape[0]})')
    plt.xlabel('Número de Estações')
    plt.ylabel('Recall (%)')
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xticks(rc_data.index, labels=[str(int(x)) for x in rc_data.index])
    plt.ylim(y_min, 100)
    plt.tight_layout()
    plt.savefig(
        'arquivos/figuras/pos_process/dist_ev_num_stations_recall_pick.png'
    )
    #plt.show()()


def hist_sta_recall_event(df, n=0, d=400, m=8):
    df = df[df['SNR_P'] > n]
    df = df[df['Distance'] < d]
    df = df[df['MLv'] < m]
    df['Num_Estacoes'] = pd.Categorical(
        df['Num_Estacoes'],
        categories=df['Num_Estacoes'].unique(),
        ordered=True
    )
    df_ = df.groupby(level='Event').first()
    df_.sort_values('Num_Estacoes', inplace=True)
    f_rel = df_['Num_Estacoes'].value_counts(normalize=True).sort_index()
    f_abs = df_['Num_Estacoes'].value_counts().sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    rc_min = 90
    rc_max = 0
    total = 0
    fig, ax = plt.subplots(figsize=(19, 8))
    for r, a in zip(f_rel.index, f_abs.index):
        f_a = f_abs.loc[a]
        freq = f_rel.loc[r] * 100
        color = sm.to_rgba(freq)
        if f_a > 0:
            total += f_a
            df_c = df_[df_['Num_Estacoes'] == r]
            descrito = df_c.describe()
            TP = df_c[(df_c['Event Pred'] == 0) & (df_c['Label'] == 0)].shape[0]
            FN = df_c[(df_c['Event Pred'] == 1) & (df_c['Label'] == 0)].shape[0]
            rc = TP / (TP + FN) * 100
            rc_max = rc if rc > rc_max else rc_max
            rc_min = rc if rc < rc_min else rc_min
            ax.bar(r, rc, color=color, edgecolor='black', width=0.5)
            ax.text(
                r, rc + 0.01, f'{rc:.2f}%',
                ha='center', va='bottom', fontsize=6, fontweight='bold'
            )
            ax.text(
                a - 0.15, rc + 0.75, f'S/N: {descrito["SNR_P"]["mean"]:.0f}±{descrito["SNR_P"]["std"]:.0f} (Q2: {descrito["SNR_P"]["50%"]:.0f})',
                ha='center', va='bottom', fontsize=7, rotation=90
            )
            ax.text(
                a, rc + 0.75, f'Dis: {descrito["Distance"]["mean"]:.0f}±{descrito["Distance"]["std"]:.0f} km',
                ha='center', va='bottom', fontsize=7, rotation=90
            )
            ax.text(
                a + 0.15, rc + 0.75, f'Mag: {descrito["MLv"]["mean"]:.2f}±{descrito["MLv"]["std"]:.2f} MLv',
                ha='center', va='bottom', fontsize=7, rotation=90
            )

        else:
            ax.bar(r, 0, color=sm.to_rgba(0), edgecolor='black', width=0.5)
            ax.text(r, 0 + 0.01, '0.00%', ha='center', va='bottom')
            ax.text(a, 0 + 1.5, '0', ha='center', va='bottom')

    cbar = fig.colorbar(sm, ax=ax)
    plt.suptitle(
        f'Recall por Número de Estações - Event Level - Total {df_.shape[0]}'
    )
    plt.title(
        f'Filtro: SNR > {n} | Distância < {d} km | MLv < {m}',
        fontsize=8
    )
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    plt.ylim(rc_min - 5, rc_max + 5)
    plt.xticks(
        sorted(df['Num_Estacoes'].unique()),
        labels=[str(i) for i in sorted(df['Num_Estacoes'].unique())])
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xlabel('Número de Estações')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig(f'arquivos/figuras/pos_process/n_sta_recall_{n}{d}{m}.png')
    # #plt.show()()


# --------------------------- SNR-P
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
        st = obspy.read(f"arquivos/mseed/{pick['Path']}")
        noise, trace_p, trace_s = prepare(
            st[0],
            filtro,
            noisewindow, pwindow, swindow
        )
        filtro.noise = np.mean(np.abs(noise))
        filtro.p = np.mean(np.abs(trace_p))
        filtro.s = np.mean(np.abs(trace_s))
        if filtro.noise == 0:
            filtro.snrp = np.nan
            filtro.snrs = np.nan
            filtro.noise = np.nan
            eventos.loc[index, 'Error'] = 'Noise = 0'
            continue
        filtro.snrp = filtro.p / filtro.noise
        filtro.snrs = filtro.s / filtro.noise
        eventos.loc[index, 'SNR_P'] = filtro.snrp
        eventos.loc[index, 'SNR_S'] = filtro.snrs
        eventos.loc[index, 'Noise'] = filtro.noise
        eventos.loc[index, 'p'] = filtro.p

    return eventos


def median_snrp_event(df):
    try:
        df.set_index(['Event', 'Station'], inplace=True)
    except KeyError:
        pass

    df['SNR_P_Q2'] = df.index.get_level_values('Event').map(
        df.reset_index().groupby('Event')['SNR_P'].median()
    )
    df['SNR_P_Q2_cat'] = pd.Categorical(
        df['SNR_P_Q2'].apply(class_snrp),
        categories=CAT_SNR,
        ordered=True
    )
    return df


def class_snrp(snrp):
    if snrp < 1:
        return '< 1'
    elif 1 <= snrp < 2:
        snr_c = 1
        while snr_c < 2:
            if snr_c <= snrp < snr_c + .25:
                return f'[{snr_c}-{snr_c + .25}['
            snr_c += .25
    elif 2 <= snrp < 15:
        snr_c = 2
        while snr_c < 15:
            if snr_c <= snrp < snr_c + 1:
                return f'[{snr_c}-{snr_c + 1}['
            snr_c += 1
    return '>= 15'


def hist_snr_recall_pick(df):
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
            TP = df_c[(df_c['Pick Pred'] == 0) & (df_c['Label'] == 0)].shape[0]
            FN = df_c[(df_c['Pick Pred'] == 1) & (df_c['Label'] == 0)].shape[0]
            rc = 100 * TP / (TP + FN) if TP + FN != 0 else 0
            ax.bar(c, rc, color=color, edgecolor='black', width=0.5, label=f'{c}')
            ax.text(c, rc + 0.01, f'{rc:.2f}%', ha='center', va='bottom', fontsize=6, fontweight='bold')
            ax.text(b, rc + 1.5, f'{f_a}', ha='center', va='bottom', fontsize=8)
            rc_min = rc if rc < rc_min else rc_min
        else:
            ax.bar(c, 0, color=sm.to_rgba(0), edgecolor='black', width=0.5)
            ax.text(c, 0 + 0.01, '0.00%', ha='center', va='bottom')
            ax.text(b, 0 + 1.5, '0', ha='center', va='bottom')

    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    plt.suptitle(f'Recall por SNR_P Pick')
    plt.title(f'Total de Picks: {total}', fontsize=8)
    plt.xticks(np.arange(len(f_rel.index)), labels=f_rel.index, rotation=90)
    plt.ylim(rc_min - 5, 105)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xlabel('SNR_P')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_process/dist_snrs_recall.png')
    # #plt.show()()


def hist_snr_recall_event(df, n=0, d=400, m=8):
    df = df[df['SNR_P'] > n]
    df = df[df['Distance'] < d]
    df = df[df['MLv'] < m]
    df = median_snrp_event(df)
    df['SNR_P_cat'] = pd.Categorical(
        df['SNR_P_cat'], categories=CAT_SNR, ordered=True
    )
    df_ = df.groupby(level='Event').first()
    f_rel = df_['SNR_P_Q2_cat'].value_counts(normalize=True).sort_index()
    f_abs = df_['SNR_P_Q2_cat'].value_counts().sort_index()
    max_freq = f_rel.max() * 100
    min_freq = f_rel.min() * 100
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='magma', norm=norm)
    sm.set_array([])
    rc_min = 90
    total = 0
    fig, ax = plt.subplots(figsize=(19, 9))
    for r, a in zip(f_rel.index, f_abs.index):
        f_a = f_abs.loc[a]
        freq = f_rel.loc[r] * 100
        median_distance = df_[df_['SNR_P_Q2_cat'] == r]['Distance'].median()
        nb_sta = df[df['SNR_P_Q2_cat'] == r].shape[0]/f_a
        color = sm.to_rgba(freq)
        if f_a > 0:
            total += f_a
            df_c = df_[df_['SNR_P_Q2_cat'] == r]
            TP = df_c[(df_c['Pick Pred'] == 0) & (df_c['Label'] == 0)].shape[0]
            FN = df_c[(df_c['Pick Pred'] == 1) & (df_c['Label'] == 0)].shape[0]
            rc = 100 * TP / (TP + FN) if TP + FN != 0 else 0
            ax.bar(r, rc, color=color, edgecolor='black', width=0.25)
            ax.text(
                r, rc + 0.01, f'{rc:.1f}%',
                ha='center', va='bottom', fontsize=7, fontweight='bold'
            )
            ax.text(
                a, rc + 3.5,
                f'#{f_a}', ha='center', va='bottom',
                fontsize=6
            )
            ax.text(
                a, rc + 2.5, f'Est.: {nb_sta:.1f}',
                ha='center', va='bottom', fontsize=6
            )
            ax.text(
                a, rc + 1.5, f'Dist.: {median_distance:.0f}km',
                ha='center', va='bottom', fontsize=6
            )
            rc_min = rc if rc < rc_min else rc_min
        else:
            ax.bar(r, 0, color=sm.to_rgba(0), edgecolor='black', width=0.5)
            ax.text(r, 0 + 0.01, '0.00%', ha='center', va='bottom')
            ax.text(a, 0 + 1.5, '0', ha='center', va='bottom')

    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    cbar.set_ticks([min_freq, max_freq])
    plt.suptitle('Recall por Média de SNR_P por Evento')
    plt.title(f'Total {df_.shape[0]} | SNR_P > {n} | Distância < {d} | MLv < {m}')
    plt.xticks(np.arange(len(f_rel.index)), labels=f_rel.index, rotation=90)
    plt.ylim(rc_min - 5, 105)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.xlabel('Média de SNR_P')
    plt.ylabel('Recall (%)')
    plt.savefig(f'arquivos/figuras/pos_process/{n}{d}{m}_dist_mean_snrs_recall.png')
    # #plt.show()()


def scatter_snr_prob(df):
    df['SNR_P_log'] = np.log10(df['SNR_P'])
    plt.figure(figsize=(10, 6))
    plt.scatter(df['SNR_P_log'], df['Pick Prob_Nat'], alpha=0.5)
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.title('Scatter Plot SNR_P x Probabilidade Natural')
    plt.xlabel('SNR_P_log')
    plt.ylabel('Probabilidade Natural')
    plt.tight_layout()
    plt.savefig('arquivos/figuras/pos_process/scatter_snrs_prob_nat.png')
    #plt.show()()


def recall_event(df, d=400, m=8):
    plt.figure(figsize=(10, 6))
    df = df[df['Distance'] < d]
    df = df[df['MLv'] < m]
    total_i = df.groupby(level='Event').first().shape[0]
    n = 0
    while n < 15:
        df = df[df['SNR_P'] > n]
        df = median_snrp_event(df)
        df['SNR_P_Q2_cat'] = pd.Categorical(
            df['SNR_P_Q2_cat'], categories=CAT_SNR, ordered=True
        )
        df.loc[:, 'SNR_P_cat'] = df['SNR_P'].apply(class_snrp)
        df.loc[:, 'SNR_P_Q2_cat'] = df['SNR_P_Q2'].apply(class_snrp)

        # by event, sum the pred_nat value and divide by the number of stations
        Events_pred = df.groupby(level='Event').apply(
            lambda x: x['Event Prob_Nat'].sum() / x.shape[0]
        )
        # if Events_pred > 0.5, then the event is classified as natural
        Events_pred = Events_pred.apply(lambda x: 0 if x > 0.5 else 1)
        # get the label of the event
        Events_label = df.groupby(level='Event').first()['Label']

        def recall_score(y_true, y_pred):
            return np.mean(y_true == y_pred)
        rec_score = recall_score(Events_label, Events_pred)
        plt.plot(n, rec_score, 'ro')
        n += 1

    total_f = df.groupby(level='Event').first().shape[0]
    plt.suptitle('Variação do Recall por Evento com SNR_P Médio Mínimo')
    plt.title(f'Total de Eventos: {total_i} ~ {total_f} | Distância < {d} | MLv < {m}')
    plt.xlabel('SNR_P')
    plt.ylabel('Recall')
    plt.tight_layout()
    plt.savefig(f'arquivos/figuras/pos_process/{d}{m}_recall_event.png')
    #plt.show()()


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
    region_origem = gpd.sjoin(
        coord_origem, regions, how='left', predicate='within'
    )
    df['Região Origem'] = region_origem['nome'].values

    return df


def region_correlation(df):
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
        x='Região Origem', y='Event Prob_Nat', data=df,
        palette=orig_colors, showfliers=False, order=order_orig,
        medianprops={'color': 'yellow'}, whiskerprops={'color': 'black'},
        meanline=True, showmeans=True, meanprops={'color': 'yellow'}
    )
    sns.stripplot(
        x='Região Origem', y='Event Prob_Nat', data=df, color='red',
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
    plt.savefig('arquivos/figuras/pos_process/region_corr.png')
    # #plt.show()()


# --------------------------- CREATE ARQUIVOS
def carregar_dado(w=3, n=0, d=400, m=8):
    df = pd.read_csv('arquivos/resultados/predito.csv')
    df = df[df['MLv'] < m]
    df = df[df['Distance'] < d]
    df.dropna(subset=['Pick Prob_Nat'], inplace=True)
    df['Label'] = df['Cat'].apply(lambda x: 0 if x == 'earthquake' else 1)
    df['Event Pred'] = df['Event Pred'].astype(int)
    df.set_index(['Event', 'Station'], inplace=True)
    df = snr(df, w)
    df = df[df['SNR_P'] > n]
    df.to_csv(f'arquivos/resultados/{w}{n}{d}{m}_analisado.csv')

    return df


# -------------------------------- MAIN ------------------------------------- #
def comercial(df):
    df_cm = df[df['Hora'] >= 11]
    df_cm = df_cm[df_cm['Hora'] < 22]

    # hist_hour_distribution(df_cm)
    hist_hour_recall_pick(df_cm)
    hist_hour_recall_event(df_cm)
    # ----------------------------------
    # hist_station_distribution(df_cm)
    hist_sta_recall_event(df_cm, 0, 400, 8)
    n = 0
    while n < 10:
        n += 0.25
        hist_sta_recall_event(df_cm, n, 400, 8)
    # ----------------------------------
    # hist_dist_distribution(df_cm)
    hist_dist_recall_event(df_cm)
    hist_dist_recall_pick(df_cm)
    # ----------------------------------
    hist_magnitude_distribution(df_cm)
    hist_magnitude_recall(df_cm)
    # ----------------------------------
    hist_snr_recall_pick(df_cm)
    # median_snr_recall_event(df_cm)
    # ----------------------------------
    plot_box_dist(df_cm)
    plot_box_by_network(df_cm)
    plot_box_by_station(df_cm)
    region_correlation(df_cm)
    return df_cm


def ncomercial(df):
    df_nc = df[(df['Hora'] < 11) | (df['Hora'] >= 22)]
    # hist_hour_recall_pick(df_nc)
    hist_hour_recall_event(df_nc)
    # ----------------------------------
    hist_sta_recall_event(df_nc, 0, 400, 8)
    n = 0
    while n < 2:
        n += 0.25
        hist_sta_recall_event(df_nc, n, 400, 8)
        while n >= 2 and n < 4:
            n += 1
            hist_sta_recall_event(df_nc, n, 400, 8)
    # ----------------------------------
    # plot_hist_distance_distribution(df)
    hist_dist_recall_pick(df_nc)
    hist_dist_recall_event(df_nc)
    box_dist_event_prob(df_nc, 0, 400, 8)
    n = 0
    while n < 2:
        n += 0.25
        box_dist_event_prob(df_nc, n, 400, 8)
        while n >= 2 and n < 10:
            n += 1
            box_dist_event_prob(df_nc, n, 400, 8)
    # ----------------------------------
    hist_magnitude_recall(df_nc)
    box_mag_event_prob(df_nc, 0, 400, 8)
    # ----------------------------------
    hist_snr_recall_pick(df_nc)
    hist_snr_recall_event(df_nc)
    # ----------------------------------
    region_correlation(df_nc)
    # ----------------------------------
    # Plot the Prob_Nat_std x Event
    # ----------------------------------
    df_nc.to_csv('arquivos/resultados/nc_analisado.csv')

    return df_nc


# -------------------------------- MAIN ------------------------------------- #
def main():
    # df = carregar_dado()
    df = pd.read_csv('arquivos/resultados/304008_analisado.csv', sep=',')
    df['Hora'] = df['Origin Time'].apply(lambda x: UTCDateTime(x).hour)
    df['Coord Origem'] = df[['Origem Latitude', 'Origem Longitude']].apply(lambda x: [x['Origem Latitude'], x['Origem Longitude']], axis=1)
    df = class_region(df)
    df = median_snrp_event(df)
    df = median_dist_event(df)

    df['Magnitude_cat'] = pd.Categorical(
        df['MLv'].apply(class_mag), categories=CAT_MAG, ordered=True
    )
    df['Distance_cat'] = pd.Categorical(
        df['Distance'].apply(class_dist), categories=CAT_DIS, ordered=True
    )
    df['SNR_P_cat'] = pd.Categorical(
        df['SNR_P'].apply(class_snrp), categories=CAT_SNR, ordered=True
    )
    df['Pick Prob_Nat_cat'] = pd.Categorical(
        df['Pick Prob_Nat'].apply(class_prob),
        categories=CAT_PROB, ordered=True
    )
    df.loc[:, 'Num_Estacoes'] = df.index.get_level_values('Event').map(
        df.reset_index().groupby('Event').size()
    )
    # calculate the std of Pick Prob_Nat by event
    df['Pick Prob_Nat_std'] = df.index.get_level_values('Event').map(
        df.groupby('Event')['Pick Prob_Nat'].std()
    )
    df['SNRP_std'] = df.index.get_level_values('Event').map(
        df.groupby('Event')['SNR_P'].std()
    )
    df['Distance_std'] = df.index.get_level_values('Event').map(
        df.groupby('Event')['Distance'].std()
    )

    df_nc = ncomercial(df)
    # df_cm = comercial(df)

    # dict_df = {

    # }

    #  subtract two lists of strings, and return a list with the differences
    # ['a', 'b', 'c'] - ['a', 'b'] = ['c']
    # ['a', 'b'] - ['a', 'b', 'c'] = []
    # ['a', 'b', 'c'] - ['a', 'b', 'c'] = []

    # df_nc = df_nc.drop(df_cm.index)
    # df_cm = df_cm.drop(df_nc.index)




    return df_nc, df


if __name__ == '__main__':
    df, df_nc = main()
