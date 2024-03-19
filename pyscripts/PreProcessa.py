import pandas as pd
# import numpy as np
# from datetime import datetime
import matplotlib.pyplot as plt
import os
from obspy import UTCDateTime


# ----------------- Functions -----------------
def list_events(events_dir):
    list_events = os.listdir(events_dir)
    return list_events


def sep_event_commercial(list_events):
    # Separete the events in two lists:
    # - events between 11am to 22pm are commercial events
    # else are non-commercial events
    commercial_events = []
    non_commercial_events = []
    for event in list_events:
        event_date = UTCDateTime(event.split('_')[0])
        if event_date.hour >= 11 and event_date.hour < 22:
            commercial_events.append(event)
        else:
            non_commercial_events.append(event)
    return commercial_events, non_commercial_events


# Plot boxplot of events hour distribution
def plot_boxplot_hour_distribution(events_list):
    hours = []
    for event in events_list:
        event_date = UTCDateTime(event.split('_')[0])
        hours.append(event_date.hour)
    plt.boxplot(hours)
    plt.title('Non-Commercial Events Hour Distribution')
    plt.ylabel('Hour')
    plt.show()


# Plot histogram of events hour distribution
def plot_hist_hour_distribution(events_list, title):
    plt.figure()
    hours = []
    for event in events_list:
        event_date = UTCDateTime(event.split('_')[0])
        hours.append(event_date.hour)
    # bins are per hour from 0 to 23
    plt.hist(hours, bins=range(0, 24), rwidth=0.8, color='b')
    plt.title(title)
    plt.xlabel('Hour')
    plt.ylabel('Frequency')
    # plt.show()
    plt.savefig('../figures/' + title + '.png')


# ----------------- Main -----------------
def main():
    event_list = list_events('../files/mseed/')
    comm, non_comm = sep_event_commercial(event_list)

    plot_hist_hour_distribution(non_comm, 'Non-Commercial Events Hour Distribution')
    plot_hist_hour_distribution(comm, 'Commercial Events Hour Distribution')

    # cria dataframe com os eventos
    df_comm = pd.DataFrame({'time': comm, 'label_cat': 0})
    df_not_comm = pd.DataFrame({'time': non_comm, 'label_cat': 0})
    # salva dataframe em arquivo csv

    df_comm.to_csv('../files/pred_commercial.csv', index=False)
    df_not_comm.to_csv('../files/pred_not_commercial.csv', index=False)
