# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/pyscripts/pre_process.py

# ---------------------------  DESCRIPTION  -----------------------------------
# Script para tratar dados anterior a classificação.
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.2
# Data: 2024-02-27
# Modificação mais recente: 2024-04-10
# Descrição: Este script será chamado antes da aquisição dos dados e apóes a
# aquisição dos dados. Ele será responsável por tratar os dados do catálogo.csv
# e dos eventos.csv. O catalogo.csv será tratado criando um
# catalogo_treated.csv que será iterado pela eventos_fluxo.py

# ----------------------------  IMPORTS   -------------------------------------
import pandas as pd
from obspy.core import UTCDateTime
import shapely.geometry
import geopandas as gpd

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

import argparse
###############################################################################
# ----------------------------  ARGUMENTS  ------------------------------------
parser = argparse.ArgumentParser(description='Pre processamento dos dados')
parser.add_argument(
    # Pode ser --eventos ou -e
    '--eventos', '-e', type=str, help='Nome do arquivo csv dos eventos'
)
parser.add_argument(
    '--catalogo', '-c', type=str, help='Nome do arquivo csv do catalogo'
)
parser.add_argument(
    '--ascending', '-a', action='store_true',
    help='Nome do arquivo csv do catalogo'
)
parser.add_argument(
    '--plot', '-p', action='store_true', help='Plotar distribuição do catalogo'
)
args = parser.parse_args()


# ----------------------------  FUNCTIONS  ------------------------------------
def brasil_catalogo(catalog: pd.DataFrame) -> pd.DataFrame:
    catalog['geometry'] = catalog.apply(
        lambda x: shapely.geometry.Point(x['Longitude'], x['Latitude']), axis=1
    )
    catalog = gpd.GeoDataFrame(catalog, geometry='geometry')
    brasil = gpd.read_file('arquivos/figuras/mapas/macrorregioesBrasil.json')
    brasil = brasil[['nome', 'geometry']]
    brasil['geometry_buffer'] = brasil.buffer(0.5)
    brasil.geometry = brasil['geometry_buffer']
    brasil.to_crs(epsg=4326, inplace=True)
    catalog.crs = brasil.crs
    catalogo_br = gpd.sjoin(
        catalog, brasil, how='inner', predicate='within'
    )
    catalogo_br = catalogo_br[
        ['EventID', 'Time', 'Depth/km', 'Author', 'Contributor', 'MagType',
         'Magnitude', 'MagAuthor', 'EventLocationName', 'EventType',
         'sigla', 'geometry']
    ]
    return catalogo_br


def profundidade_catalogo(catalog: pd.DataFrame) -> pd.DataFrame:
    catalog = catalog[catalog['depth'] < 100]
    return catalog


def order_catalog(catalog: pd.DataFrame,
                  ascending: bool) -> pd.DataFrame:
    catalog['Time'] = pd.to_datetime(catalog['Time'])
    catalog = catalog.sort_values(by='Time', ascending=ascending)

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
    pred_eq.to_csv('arquivos/predcsv/pred_earthquake.csv', index=False)
    pred.to_csv('arquivos/predcsv/pred.csv', index=False)


def filter_pred_com(pred: pd.DataFrame) -> pd.DataFrame:
    pred['Hora'] = pred['Event'].apply(lambda x: UTCDateTime(x).hour)
    pred_com = pred[(pred['Hora'] >= 11) & (pred['Hora'] < 22)]
    pred_nc = pred[(pred['Hora'] < 11) | (pred['Hora'] >= 22)]
    pred_com = pred_com.drop(columns=['Hora'])
    pred_nc = pred_nc.drop(columns=['Hora'])
    pred_com.to_csv('arquivos/predcsv/pred_commercial.csv', index=False)
    pred_nc.to_csv('arquivos/predcsv/pred_no_commercial.csv', index=False)

    return pred, pred_com, pred_nc


def check_ev_id():
    old_c = pd.read_csv('arquivos/catalogo/Catalog.csv', sep=';')
    c = pd.read_csv(
        'arquivos/catalogo/catalogo-moho-south-america.csv',
        sep='|'
    )
    oldids = old_c['EventID'].to_list()
    ids = c['EventID'].to_list()
    for i in oldids:
        if i not in ids:
            print(i)


# ----------------------------  PLOT  -----------------------------------------
def plot_distrib_hora(
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
    plt.savefig('arquivos/figures/pre_process/histogramas/hist_hora.png')
    plt.show()


def plot_out_of_brasil_as_red(catalog: pd.DataFrame) -> None:
    catalog.drop_duplicates(subset='EventID', inplace=True)
    catalog = gpd.GeoDataFrame(
        catalog,
        geometry=gpd.points_from_xy(catalog.Longitude, catalog.Latitude)
    )
    catalog.crs = 'EPSG:4326'
    brasil = gpd.read_file('arquivos/figuras/mapas/macrorregioesBrasil.json')
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


def plot_prof_as_red(catalog: pd.DataFrame) -> None:
    catalog.drop_duplicates(subset='EventID', inplace=True)
    catalog = gpd.GeoDataFrame(
        catalog,
        geometry=gpd.points_from_xy(catalog.Longitude, catalog.Latitude)
    )
    catalog.crs = 'EPSG:4326'
    brasil = gpd.read_file('arquivos/figuras/mapas/macrorregioesBrasil.json')
    brasil.to_crs(epsg=4326, inplace=True)
    brasil = brasil.geometry.unary_union
    catalog['color'] = 'blue'
    catalog.loc[catalog['depth'] > 200, 'color'] = 'red'
    fig, ax = plt.subplots()
    catalog.plot(ax=ax, color=catalog['color'], markersize=10)
    gpd.GeoSeries([brasil]).boundary.plot(ax=ax, color='black')
    plt.title('Seismic Events: Red if outside Brazil, Blue if inside')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()


# ----------------------------  MAIN  -----------------------------------------
def main(args=args):
    if args.catalogo:
        catalog = pd.read_csv(f'arquivos/catalogo/{args.catalogo}', sep=',')
        # catalog = brasil_catalogo(catalog)
        catalog = profundidade_catalogo(catalog)
        catalog = order_catalog(catalog, args.ascending)
        catalog.to_csv(
            f'arquivos/catalogo/{args.catalogo}_treated.csv', index=False
        )
    elif args.eventos:
        events = pd.read_csv(f'arquivos/eventos/{args.eventos}', sep=',')
        gerar_predcsv(events)
        pred, pred_com, pred_nc = filter_pred_com(events)
    else:
        print('Nenhum arquivo catalogo foi passado')

    return catalog


if __name__ == '__main__':
    catalog = main()
