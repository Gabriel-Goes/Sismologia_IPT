import pandas as pd
# import numpy as np
# from datetime import datetime
import matplotlib.pyplot as plt
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


# Plot histogram of events hour distribution
def plot_hist_hour_distribution(events_list, title):
    hours = []
    plt.figure(figsize=(9, 6))
    for event in events_list:
        event_date = UTCDateTime(event.split('_')[0])
        hours.append(event_date.hour)
    print(f'{set(hours)}')

    # bins are per hour from 0 to 23
    plt.hist(hours, bins=range(0, 25), rwidth=0.8, color='b')
    # Ajustando os ticks do eixo x para que fiquem a 0.5 para a direita de cada número inteiro
    tick_positions = [x + 0.5 for x in range(24)]
    plt.xticks(tick_positions, [str(i) for i in range(24)])

    # Only horizontal grid lines
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.gca().xaxis.grid(False)
    plt.title(title)
    plt.xlabel('Hour')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig('./figures/' + title + '.png')
    plt.show()
    plt.close()
    return hours


def get_true_false(validation):
    '''
                    event  label_cat  prob_nat  prob_ant  pred         nature
    0     20200330T033011          0     0.979     0.021     0        Natural
    1     20180311T081623          0     0.993     0.007     0        Natural
    2     20190109T085554          0     0.984     0.016     0        Natural
    3     20151116T053444          0     0.472     0.528     1  Anthropogenic
    4     20210512T103742          0     0.938     0.062     0        Natural
    ...               ...        ...       ...       ...   ...             ...
    '''
    # Create functions to analyze the results of the model from prob_ant and event time
    # - Create a list of events with prob_ant > 0.75
    # - Create a list of events with prob_ant < 0.25
    # - Create a list of events with prob_ant between 0.25 and 0.75

    # leitura dos arquivos csv files/output/non_commercial/validation_network_level.csv
    df_val = pd.read_csv('files/output/' + validation)
    print(f' - non_comm_net: {df_val.shape}')

    ant_high_certainty = df_val[df_val['prob_ant'] > 0.75]
    nat_high_certainty = df_val[df_val['prob_ant'] < 0.25]

    return ant_high_certainty, nat_high_certainty


def classify_magnitude(mag):
    if mag < 1:
        return '<1'
    elif 1 <= mag < 2:
        return '[1-2['
    elif 2 <= mag < 3:
        return '[2-3['
    else:
        return '>=3'

def plot_hist_magnitude_distribution(df_merged):
    plt.figure(figsize=(10, 6))
    # Organiza o plot em ordem crescente de magnitude
    # >1, [1-2[, [2-3[, >=3
    df_merged['magnitude_category'] = pd.Categorical(df_merged['magnitude_category'],
                                                     categories=['<1', '[1-2[', '[2-3[', '>=3'],
                                                     ordered=True)
    df_merged['magnitude_category'].value_counts().sort_index().plot(kind='bar', color='b')

    plt.title('Distribuição de Eventos por Categoria de Magnitude')
    plt.xlabel('Categoria de Magnitude')
    plt.ylabel('Número de Eventos')
    plt.tight_layout()
    plt.show()


# Plot histogram of magnitude distribution by recall
# df_merged['pred'] and def_merged['nature']
def plot_hist_magnitude_distribution_recall(df_merged):
    plt.figure(figsize=(10, 6))
    # Organiza o plot em ordem crescente de magnitude
    categories = ['<1', '[1-2[', '[2-3[', '>=3']
    df_merged['magnitude_category'] = pd.Categorical(df_merged['magnitude_category'],
                                                     categories=categories,
                                                     ordered=True)
    # yaxis is the recall
    # recall = TP / (TP + FN)
    # TP = pred == 1 and nature == 1
    # FN = pred == 0 and nature == 1
    # Get the accuracy of the magnitude category '<1'
    for category in categories:
        print(f'Category: {category}')
        mag_cat = df_merged[df_merged['magnitude_category'] == category]
        TP = mag_cat[(mag_cat['pred'] == 0) & (mag_cat['label_cat'] == 0)].shape[0]
        FN = mag_cat[(mag_cat['pred'] == 1) & (mag_cat['label_cat'] == 0)].shape[0]
        print(f'TP: {TP}, FN: {FN}')
        recall = TP / (TP + FN)
        print(f'recall: {recall}')
        plt.bar(category, recall, color='b')

    # Make the y axis start at 0.6
    plt.ylim(0.6, 1)
    # grids
    plt.gca().yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')

    plt.title('Distribuição de Eventos por Categoria de Magnitude')
    plt.xlabel('Categoria de Magnitude')
    plt.ylabel('Recall')
    plt.tight_layout()
    plt.show()


# ----------------- Main -----------------
def main():
    not_comm = list_events('./files/predcsv/pred_not_commercial.csv')
    x, not_comm_23 = sep_event_commercial(not_comm)
    hours_23 = plot_hist_hour_distribution(not_comm_23,
                                           'NON-COMMERCIAL ( 11 to 23 UTC )')
    hours_22 = plot_hist_hour_distribution(not_comm,
                                           'NON-COMMERCIAL ( 11 to 22 UTC )')

    catalogo_moho = pd.read_csv('./files/catalogo/events-moho-catalog.csv')
    catalogo_moho['event'] = catalogo_moho['Folder']

    df_val = pd.read_csv('files/output/non_commercial/validation_network_level.csv')
    df_merged = pd.merge(df_val, catalogo_moho, on='event', how='left')
    df_merged['magnitude_category'] = df_merged['MLv'].apply(classify_magnitude)

    plot_hist_magnitude_distribution(df_merged)

    plot_hist_magnitude_distribution_recall(df_merged)

    
    return catalogo_moho, df_merged, hours_23, hours_22, x


if __name__ == '__main__':
    main()














