# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/pyscripts/pre_process.py

# ---------------------------  DESCRIPTION  -----------------------------------
# Script para tratar dados anterior a classificação.
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.2
# Data: 2024-02-27
# Modificação mais recente: 2024-04-10

# ----------------------------  IMPORTS   -------------------------------------
import pandas as pd
from obspy.core import UTCDateTime
import shapely.geometry
import geopandas as gpd

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
###############################################################################


# ----------------------------  FUNCTIONS  ------------------------------------
def brasil_catalogo(catalog: pd.DataFrame) -> pd.DataFrame:
    catalog['geometry'] = catalog.apply(
        lambda x: shapely.geometry.Point(x['Longitude'], x['Latitude']), axis=1
    )
    catalog = gpd.GeoDataFrame(catalog, geometry='geometry')
    brasil = gpd.read_file('files/figures/maps/macrorregioesBrasil.json')
    brasil.to_crs(epsg=4326, inplace=True)
    catalog.crs = brasil.crs
    c_brasil = gpd.sjoin(
        catalog, brasil, how='inner', predicate='within'
    )
    c_brasil = c_brasil[
        ['EventID', 'Time', 'Depth/km', 'Author', 'Contributor', 'MagType',
         'Magnitude', 'MagAuthor', 'EventLocationName', 'EventType',
         'sigla', 'geometry']
    ]
    return c_brasil


def order_catalog(catalog: pd.DataFrame) -> pd.DataFrame:
    catalog['Time'] = pd.to_datetime(catalog['Time'])
    catalog = catalog.sort_values(by='Time', ascending=False)
    catalog = catalog[catalog['Time'] > '2000-01-01']

    return catalog


def gerar_predcsv(events: pd.DataFrame) -> [pd.DataFrame]:
    events_eq = events[events['Cat'] == 'earthquake']
    pred_eq = events_eq[['Event', 'Cat']]
    pred = events[['Event', 'Cat']]
    pred_eq['Cat'] = pred_eq['Cat'].apply(
        lambda x: 0 if x == 'earthquake' else 1
    )
    pred['Cat'] = events['Cat'].apply(
        lambda x: 0 if x == 'earthquake' else 1
    )
    pred_eq.to_csv('files/predcsv/pred_earthquake.csv', index=False)
    pred.to_csv('files/predcsv/pred.csv', index=False)


def filter_pred_com(pred: pd.DataFrame) -> pd.DataFrame:
    pred['Hora'] = pred['Event'].apply(lambda x: UTCDateTime(x).hour)
    pred_com = pred[(pred['Hora'] >= 11) & (pred['Hora'] < 22)]
    pred_nc = pred[(pred['Hora'] < 11) | (pred['Hora'] >= 22)]
    pred_com = pred_com.drop(columns=['Hora'])
    pred_nc = pred_nc.drop(columns=['Hora'])
    pred_com.to_csv('files/predcsv/pred_commercial.csv', index=False)
    pred_nc.to_csv('files/predcsv/pred_no_commercial.csv', index=False)

    return pred, pred_com, pred_nc


# ----------------------------  PLOT  -----------------------------------------
def catalog_dist(catalog, att: str = 'sigla'):
    ax = catalog.plot(
        column=att, categorical=True,  markersize=1, figsize=(10, 10)
    )
    ax.set_title('Distribuição de eventos sísmicos no Brasil')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.show()

    return


def pred_hora_dist(
        pred: pd.DataFrame) -> None:
    counts = pred['Hora'].value_counts(sort=False).reindex(
        np.arange(24), fill_value=0
    )
    density = counts / counts.sum()
    plt.figure(figsize=(10, 6))
    colors = ['blue' if (11 <= hour < 22) else 'red' for hour in counts.index]
    bars = plt.bar(counts.index, density, color=colors, alpha=0.5, width=0.8)
    for b, l in zip(bars, counts):
        yval = b.get_height()
        plt.text(
            b.get_x() + b.get_width() / 2,
            yval + 0.001,
            int(l),
            ha='center',
            va='bottom'
        )
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    plt.xticks(range(0, 24))
    plt.grid(axis='y')
    plt.title('Distribuição de eventos sísmicos por hora (UTC)')
    plt.xlabel('Hora (UTC)')
    plt.ylabel('Frequência')
    plt.legend(
        ['Horário Comercial', 'Fora do Horário Comercial'], loc='upper right')
    plt.savefig('files/figures/pre_process/histogramas/hist_hora.png')
    plt.show()


def pre_process_catalog(csv: str) -> None:
    catalog = pd.read_csv(f'files/catalogo/{csv}.csv', sep='|')
    catalog = brasil_catalogo(catalog)
    catalog = order_catalog(catalog)
    catalog.reset_index(drop=True, inplace=True)
    catalog.to_csv(f'files/catalogo/{csv}_treated.csv', index=False)

    catalog_dist(catalog, 'Author')

    return catalog


# ----------------------------  MAIN  -----------------------------------------

def check_ev_id():
    old_c = pd.read_csv('files/catalogo/Catalog.csv', sep=';')
    c = pd.read_csv('files/catalogo/catalogo-moho-south-america.csv', sep='|')
    oldids = old_c['EventID'].to_list()
    ids = c['EventID'].to_list()
    for i in oldids:
        if i not in ids:
            print(i)


def plot_out_of_brasil_as_red(catalog: pd.DataFrame) -> None:
    catalog.drop_duplicates(subset='EventID', inplace=True)
    catalog = gpd.GeoDataFrame(
        catalog,
        geometry=gpd.points_from_xy(catalog.Longitude, catalog.Latitude)
    )
    catalog.crs = 'EPSG:4326'
    brasil = gpd.read_file('files/figures/maps/macrorregioesBrasil.json')
    brasil.to_crs(epsg=4326, inplace=True)
    brasil = brasil.geometry.unary_union
    catalog['color'] = 'blue'
    catalog.loc[~catalog.geometry.within(brasil), 'color'] = 'red'
    fig, ax = plt.subplots()
    catalog.plot(ax=ax, color=catalog['color'], markersize=10)
    gpd.GeoSeries([brasil]).boundary.plot(ax=ax, color='black')
    plt.title('Seismic Events: Red if outside Brazil, Blue if inside')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()
