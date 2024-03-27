import pandas as pd
# from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

import os
from obspy import UTCDateTime
# import obspy


# ----------------- Functions -----------------
# Read mseed file
def list_events_dir(events_dir):
    list_events = os.listdir(events_dir)
    return list_events


# Read pred_csv file
def list_events(pred_csv):
    list_events = pd.read_csv(pred_csv)
    return list_events['time'].tolist()


def sep_event_commercial(list_events):
    # Separete the events in two lists:
    # - events between 11am to 22pm are commercial events
    # else are non-commercial events
    commercial_events = []
    non_commercial_events = []
    for event in list_events:
        event_date = UTCDateTime(event.split('_')[0])
        if event_date.hour >= 11 and event_date.hour < 23:
            commercial_events.append(event)
        else:
            non_commercial_events.append(event)
    return commercial_events, non_commercial_events


# remove commercial_events from dataframe
def remove_commercial_events(df, commercial_events):
    for event in commercial_events:
        df = df[df['event'] != event]
    return df


def get_true_false(validation):
    # leitura dos arquivos csv files/output/non_commercial/validation_network_level.csv
    df_val = pd.read_csv('files/output/' + validation)
    print(f' - non_comm_net: {df_val.shape}')

    ant_high_certainty = df_val[df_val['prob_ant'] > 0.75]
    nat_high_certainty = df_val[df_val['prob_ant'] < 0.25]

    return ant_high_certainty, nat_high_certainty


# ---------------------------- Plots ----------------------------------------- #
# Correlation Matrix
def plot_corr_matrix(df):
    cols = ['prob_nat', 'Hour',
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
    plt.savefig('./figures/corr_matrix.png')
    plt.show()


# ---------------------------- ScatterPlots ---------------------------------- #
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
    plt.savefig('./figures/scatter_plot.png')
    plt.show()


def plot_facetgrid(df, x, y, hue):
    df = df[['pred', 'prob_nat', 'Hour',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    g = sns.FacetGrid(df, hue=hue, height=5)
    g = g.map(plt.scatter, x, y, edgecolor="w").add_legend()
    plt.savefig('./figures/facetgrid_scatter.png')
    plt.show()


def plot_pairplot(df):
    df = df[['pred', 'prob_nat', 'Hour',
             'MLv', 'Distance', 'Num_Estacoes']]
    sns.pairplot(df, hue='pred')
    plt.savefig('./figures/pairplot.png')
    plt.show()


def plot_jointplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hour',
             'Longitude', 'Latitude', 'distance_category',
             'MLv', 'Distance', 'Num_Estacoes']]
    sns.jointplot(x=x, y=y, data=df, kind='scatter', hue='pred')
    plt.ylim(df[y].min() - 2, df[y].max() + 2)
    plt.xlim(df[x].min() - 0.5, df[x].max() + 0.5)
    plt.xticks(range(int(df[x].min()), int(df[x].max()) + 1))
    plt.yticks(range(int(df[y].min()), int(df[y].max()) + 1))
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.savefig('./figures/jointplot.png')
    plt.show()


def plot_lmplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hour',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    sns.lmplot(x=x, y=y, data=df, hue='pred')
    plt.savefig('./figures/lmplot.png')
    plt.show()


def plot_regplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hour',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    sns.regplot(x=x, y=y, data=df,)
    plt.savefig('./figures/regplot.png')
    plt.show()


def plot_swarmplot(df, x, y, natural=True):
    df = df[['pred', 'prob_nat', 'Hour',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    if not natural:
        df = df[df['pred'] == 1]
        sns.swarmplot(x=x, y=y, data=df, size=2.5, color='red')
    else:
        sns.swarmplot(x=x, y=y, data=df, size=2.5, hue='pred')
    plt.savefig('./figures/swarmplot.png')
    plt.show()


def plot_stripplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hour',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    sns.stripplot(x=x, y=y, data=df, size=2.5, hue='pred')
    plt.savefig('./figures/stripplot.png')
    plt.show()


def plot_boxplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hour',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    sns.boxplot(x=x, y=y, data=df, hue='pred')
    plt.savefig('./figures/boxplot.png')
    plt.show()


def plot_violinplot(df, x, y):
    df = df[['pred', 'prob_nat', 'Hour',
             'Longitude', 'Latitude', 'MLv', 'Distance', 'Num_Estacoes']]
    sns.violinplot(x=x, y=y, data=df, hue='pred')
    plt.savefig('./figures/violinplot.png')
    plt.show()


# ---------------------------- Histograms ------------------------------------ #
def plot_hist_kde(df, column):
    cols = ['prob_nat', 'Hour',
            'Longitude', 'Latitude',
            'MLv', 'Distance', 'Num_Estacoes']
    df = df[cols]
    sns.histplot(df[column], kde=True, color='lightskyblue')
    plt.title(f'Distribuição de {column}')
    plt.tight_layout()
    plt.savefig(f'./figures/hist_kde_{column}.png')
    plt.show()


# --------------------------------- Hours
# Plot histogram of events hour distribution
def plot_hist_hour_distribution(events_list, time):
    hours = []
    plt.figure(figsize=(9, 6))
    for event in events_list:
        event_date = UTCDateTime(event.split('_')[0])
        hours.append(event_date.hour)
    print(f'{set(hours)}')

    # bins are per hour from 0 to 23
    plt.hist(hours, bins=range(0, 25), rwidth=0.8, color='lightskyblue')
    # Ajustando os ticks do eixo x para que fiquem a 0.5 para a direita de cada número inteiro
    tick_positions = [x + 0.5 for x in range(24)]
    plt.xticks(tick_positions, [str(i) for i in range(24)])

    # Only horizontal grid lines
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.gca().xaxis.grid(False)
    plt.title('Distribuição de Eventos por Hora - 11am ~ ' + time + ' UTC')
    plt.xlabel('Hour')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig('./figures/hist_ev_hour' + time + '.png')
    plt.show()
    plt.close()
    return hours


def classify_hour(hour):
    if 0 <= hour < 2:
        return '[0-2['
    elif 2 <= hour < 4:
        return '[2-4['
    elif 4 <= hour < 6:
        return '[4-6['
    elif 6 <= hour < 8:
        return '[6-8['
    elif 8 <= hour < 10:
        return '[8-10['
    elif 10 <= hour < 12:
        return '[10-12['
    elif 12 <= hour < 14:
        return '[12-14['
    elif 14 <= hour < 16:
        return '[14-16['
    elif 16 <= hour < 18:
        return '[16-18['
    elif 18 <= hour < 20:
        return '[18-20['
    elif 20 <= hour < 22:
        return '[20-22['
    else:
        return '[22-24['


# Plot histogram of events hour distribution by recall
def plot_hist_hour_distribution_recall(df):
    fig, ax = plt.subplots(figsize=(9, 6))
    df['Hora de Origem (UTC)'] = df['Hora de Origem (UTC)'].apply(UTCDateTime)
    df['Hour'] = df['Hora de Origem (UTC)'].apply(lambda x: x.hour)
    df['Hour by 2'] = df['Hour'].apply(classify_hour)
    hour_category = pd.CategoricalDtype(categories=[
                                        0, 1, 2, 3, 4, 5, 6, 7, 8,
                                        9, 10, 22, 23],
                                        ordered=True)
    df['Hour'] = pd.Categorical(df['Hour'], dtype=hour_category)
    freq_relative = df['Hour'].value_counts(normalize=True).sort_index()
    max_freq = freq_relative.max() * 100
    norm = mcolors.Normalize(vmin=0, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=norm)
    sm.set_array([])  # Empty array for the ScalarMappable
    for hour in df['Hour'].cat.categories:
        hour_df = df[df['Hour'] == hour]
        TP = hour_df[(hour_df['pred'] == 0) & (hour_df['label_cat'] == 0)].shape[0]
        FN = hour_df[(hour_df['pred'] == 1) & (hour_df['label_cat'] == 0)].shape[0]
        if TP + FN == 0:
            print('')
            print(f'hour: {hour} TP: {TP} FN: {FN}')
            print('')
            print(hour_df)
            print('')
            continue
        recall = TP / (TP + FN) * 100
        frequency = freq_relative.loc[hour] * 100
        color = sm.to_rgba(frequency)
        ax.text(hour_df['Hour'].cat.categories.get_loc(hour),
                recall + 0.01, f'{recall:.2f}',
                ha='center', va='bottom', color='black')
        ax.bar(hour, recall, color=color)
    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    plt.xticks(range(len(df['Hour'].cat.categories)), df['Hour'].cat.categories)
    plt.xticks(range(0, 24, 1))
    plt.ylim(70, 100)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.gca().xaxis.grid(False)
    plt.title('Distribuição de Eventos por Hora')
    plt.xlabel('Hora')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('./figures/hist_ev_hour_recall.png')
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
    plt.savefig('./figures/dist_ev_distance_rel_freq.png')
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

    # Organize the plot in ascending order of distance
    categories = ['<50', '[50-100[', '[100-150[', '[150-200[', '[200-250[', '[250-300[', '>=300']
    df['distance_category'] = pd.Categorical(df['distance_category'],
                                             categories=categories,
                                             ordered=True)

    # Calculate the relative frequency for each category
    freq_relative = df['distance_category'].value_counts(normalize=True).sort_index()

    # Calcula o valor máximo para a escala de cor
    max_freq = freq_relative.max() * 100  # converte para porcentagem

    # Cria o ScalarMappable com a escala de cor normalizada
    norm = mcolors.Normalize(vmin=0, vmax=max_freq)
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=norm)
    sm.set_array([])  # Array vazio para o ScalarMappable
    # Create a colormap

    for category in categories:
        cat_df = df[df['distance_category'] == category]
        TP = cat_df[(cat_df['pred'] == 0) & (cat_df['label_cat'] == 0)].shape[0]
        FN = cat_df[(cat_df['pred'] == 1) & (cat_df['label_cat'] == 0)].shape[0]
        recall = TP / (TP + FN) * 100
        frequency = freq_relative.loc[category] * 100
        color = sm.to_rgba(frequency)
        # anotate at the top of the bar the recall value
        ax.text(categories.index(category),
                recall + 0.01, f'{recall:.2f}',
                ha='center', va='bottom', color='black')
        ax.bar(category, recall, color=color)
    # Adiciona a colorbar ao plot
    cbar = fig.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('Frequency (%)')
    # Horizontal grid lines and x-ticks
    plt.ylim(65, 100)
    plt.xticks(range(len(categories)), categories)
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.gca().xaxis.grid(False)
    # plt.title('Distance Distribution of Events')
    plt.xlabel('Epicentral Distance (km)')
    plt.ylabel('Recall (%)')
    plt.tight_layout()
    plt.savefig('./figures/hist_ev_distance.png')
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
    plt.savefig('./figures/dist_ev_cat_mag.png')
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
    plt.savefig('./figures/dist_ev_cat_mag_recall.png')
    plt.show()


# -------------------------- Number of Stations
def plot_hist_station_dist(df):
    plt.figure(figsize=(10, 6))
    # Histograma com frequências absolutas
    df['Num_Estacoes'].value_counts().sort_index().plot(kind='bar', color='lightskyblue')
    # Anotate the top of the bar the frequency value
    for i, v in enumerate(df['Num_Estacoes'].value_counts().sort_index()):
        plt.text(i, v, str(v), ha='center', va='bottom', color='black')
    # Ajustando os ticks do eixo x para que fiquem a 0.5 para a direita de cada número inteiro
    plt.xticks(range(len(df['Num_Estacoes'].unique())), df['Num_Estacoes'].unique())
    # Adicionando gridlines horizontais
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.title('Distribuição de Eventos por Número de Estações')
    plt.xlabel('Número de Estações')
    plt.ylabel('Número de Eventos')
    plt.tight_layout()
    plt.savefig('./figures/dist_ev_num_stations_absoluto.png')
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
    plt.savefig('./figures/dist_ev_num_stations_recall.png')
    plt.show()


# -------------------------------- Main -------------------------------------- #
def main_non_commercial():
    catalogo_moho = pd.read_csv('./files/events-moho-catalog.csv')
    catalogo_moho.rename(columns={'Folder': 'event'}, inplace=True)
    not_comm = list_events('./files/predcsv/pred_not_commercial.csv')
    comm_23, ncomm_23 = sep_event_commercial(not_comm)

    # get the attributes of moho_catalog and append to df_ncomm_val
    df_ncomm = pd.read_csv('files/output/non_commercial/validation_network_level.csv')
    # df_ncomm_val_23 = remove_commercial_events(df_ncomm_val, comm_23)
    df_ncomm_merged = pd.merge(df_ncomm, catalogo_moho,
                               on='event', how='left')
    # Get only the nearest station of each event
    df_ncomm_merged['Num_Estacoes'] = df_ncomm_merged.groupby('ID')['ID'].transform('count')
    df_ncomm_merged.sort_values(by=['event', 'Distance'], inplace=True)
    df_ncomm_nearest = df_ncomm_merged.drop_duplicates(subset=['event'],
                                                       keep='first')

    # Histograma de eventos por hora
    plot_hist_hour_distribution(ncomm_23, '23')
    df_ncomm_nearest = plot_hist_hour_distribution_recall(df_ncomm_nearest)

    # Histogram by number of stations
    plot_hist_station_dist(df_ncomm_nearest)
    plot_hist_num_stations_recall(df_ncomm_nearest)

    # Histogram - Frequency of Distances ( nearest station of event)
    plot_hist_distance_frequency(df_ncomm_nearest)

    # Histograma mergeddistancia
    df_ncomm_nearest.loc[:, 'distance_category'] =\
        df_ncomm_nearest['Distance'].apply(classify_distance)

    plot_hist_distance_recall(df_ncomm_nearest)

    # histograma categoria de magnitude por recall
    df_ncomm_nearest.loc[:, 'magnitude_category'] =\
        df_ncomm_nearest['MLv'].apply(classify_magnitude)

    plot_hist_magnitude_distribution_recall(df_ncomm_nearest)

    return comm_23, ncomm_23, df_ncomm_merged, df_ncomm_nearest, catalogo_moho


def main_commercial():
    catalogo_moho = pd.read_csv('./files/events-moho-catalog.csv')
    catalogo_moho.rename(columns={'Folder': 'event'}, inplace=True)
    comm = list_events('./files/predcsv/pred_commercial.csv')

    # get the attributes of moho_catalog and append to df_comm_val
    df_comm_val = pd.read_csv('files/output/commercial/validation_network_level.csv')
    df_comm_val = remove_commercial_events(df_comm_val, comm)
    df_comm_val_merged = pd.concat(df_comm_val, catalogo_moho,
                                   on='event', how='left')

    df_comm_val_merged.sort_values(by=['ID', 'Distance'], inplace=True)
    df_comm_nearest = df_comm_val_merged.drop_duplicates(subset=['ID'],
                                                         keep='first')

    return df_comm_val_merged, df_comm_nearest, catalogo_moho


if __name__ == '__main__':
    main_non_commercial()
    # main_commercial()
