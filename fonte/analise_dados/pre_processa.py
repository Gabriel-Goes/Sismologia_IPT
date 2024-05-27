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
import pygmt

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

import argparse


###############################################################################
# ----------------------------  ARGUMENTS  ------------------------------------
parser = argparse.ArgumentParser(description='Pre processamento dos dados')
parser.add_argument(
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
    brasil = brasil[['geometry']]
    brasil.to_crs(epsg=32623, inplace=True)
    brasil['geometry_buffer'] = brasil.buffer(400000)
    brasil.set_geometry('geometry_buffer', inplace=True)
    union_br = brasil.unary_union
    brasil_b = gpd.GeoDataFrame(geometry=[union_br], crs='EPSG:32623')
    brasil_b.to_crs(epsg=4326, inplace=True)
    catalog.crs = brasil_b.crs
    catalogo_br = gpd.sjoin(
        catalog, brasil_b, how='inner', predicate='within'
    )
    catalogo_br.drop(columns=['index_right'], inplace=True)
    return catalogo_br


def profundidade_catalogo(catalog: pd.DataFrame) -> pd.DataFrame:
    catalog = catalog[catalog['Depth/km'] < 100]
    return catalog


def order_catalog(catalog: pd.DataFrame,
                  ascending: bool) -> pd.DataFrame:
    catalog['Time'] = pd.to_datetime(catalog['Time'])
    catalog = catalog.sort_values(by='Time', ascending=ascending)

    return catalog


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
    catalog.drop_duplicates(subset='#EventID', inplace=True)
    catalog = gpd.GeoDataFrame(
        catalog,
        geometry=gpd.points_from_xy(catalog.Longitude, catalog.Latitude)
    )
    catalog.crs = 'EPSG:4326'
    brasil = gpd.read_file('arquivos/figuras/mapas/macrorregioesBrasil.json')
    brasil.to_crs(epsg=4326, inplace=True)
    brasil = brasil.geometry.unary_union
    catalog['color'] = 'blue'
    catalog.loc[catalog['Depth/km'] > 1, 'color'] = 'green'
    catalog.loc[catalog['Depth/km'] > 50, 'color'] = 'yellow'
    catalog.loc[catalog['Depth/km'] > 100, 'color'] = 'orange'
    catalog.loc[catalog['Depth/km'] > 200, 'color'] = 'red'
    nb_ev_blue = catalog[catalog['Depth/km'] <= 1].shape[0]
    nb_ev_1 = catalog[(catalog['Depth/km'] > 1) & (catalog['Depth/km'] <= 50)].shape[0]
    nb_ev_50 = catalog[(catalog['Depth/km'] > 50) & (catalog['Depth/km'] <= 100)].shape[0]
    nb_ev_100 = catalog[(catalog['Depth/km'] > 100) & (catalog['Depth/km'] <= 200)].shape[0]
    nb_ev_200 = catalog[catalog['Depth/km'] > 200].shape[0]
    fig = pygmt.Figure()
    fig.coast(shorelines='1/0.5p', projection="M10i", region=[-75, -30, -35, 5], borders=[1], area_thresh=10000, land="gray", water="skyblue")
    fig.basemap(
        frame=['a4f3g6', "+t\"Eventos Sismológicos pré-tratamento por Profundidade (km)\""]
    )
    fig.plot(x=catalog[catalog['Depth/km'] <= 1].Longitude,
             y=catalog[catalog['Depth/km'] <= 1].Latitude,
             style="c0.1c", fill="blue", label=f"Profundidade <= 1 km ({nb_ev_blue})")
    fig.plot(x=catalog[(catalog['Depth/km'] > 1) & (catalog['Depth/km'] <= 50)].Longitude,
             y=catalog[(catalog['Depth/km'] > 1) & (catalog['Depth/km'] <= 50)].Latitude,
             style="c0.2c", fill="green", label=f"Profundidade 1 - 50 km ({nb_ev_1})")
    fig.plot(x=catalog[(catalog['Depth/km'] > 50) & (catalog['Depth/km'] <= 100)].Longitude,
             y=catalog[(catalog['Depth/km'] > 50) & (catalog['Depth/km'] <= 100)].Latitude,
             style="c0.2c", fill="yellow", label=f"Profundidade 50 - 100 km ({nb_ev_50})")
    fig.plot(x=catalog[(catalog['Depth/km'] > 100) & (catalog['Depth/km'] <= 200)].Longitude,
             y=catalog[(catalog['Depth/km'] > 100) & (catalog['Depth/km'] <= 200)].Latitude,
             style="c0.2c", fill="orange", label=f"Profundidade 100 - 200 km ({nb_ev_100})")
    fig.plot(x=catalog[catalog['Depth/km'] > 200].Longitude,
             y=catalog[catalog['Depth/km'] > 200].Latitude,
             style="c0.2c", fill="red", label=f"Profundidade > 200 km ({nb_ev_200})")
    fig.legend(position="JBR+jBR+o0.5c/0.5c", box="+gwhite+p1p,black")
    fig.text(x=-52, y=8, text="Eventos Sismológicos pré-tratamento por Profundidade (km)", font="16p,Helvetica-Bold")
    fig.savefig('arquivos/figuras/pre_process/mapas/mapa_eventos_bruto.png')
    fig.show()


def plot_cleaned_catalog_pygmt(catalog: pd.DataFrame) -> None:
    catalog = gpd.GeoDataFrame(
        catalog,
        geometry=gpd.points_from_xy(catalog.Longitude, catalog.Latitude)
    )
    catalog.crs = 'EPSG:4326'
    catalog['color'] = 'blue'
    catalog.loc[catalog['Depth/km'] > 1, 'color'] = 'green'
    catalog.loc[catalog['Depth/km'] > 5, 'color'] = 'orange'
    catalog.loc[catalog['Depth/km'] > 25, 'color'] = 'red'
    nb_ev_blue = catalog[catalog['Depth/km'] <= 1].shape[0]
    nb_ev_1 = catalog[(catalog['Depth/km'] > 1) & (catalog['Depth/km'] <= 5)].shape[0]
    nb_ev_5 = catalog[(catalog['Depth/km'] > 5) & (catalog['Depth/km'] <= 25)].shape[0]
    nb_ev_25 = catalog[(catalog['Depth/km'] > 25) & (catalog['Depth/km'] <= 50)].shape[0]
    fig = pygmt.Figure()
    fig.coast(
        shorelines='1/0.5p', projection="M10i", region=[-75, -30, -35, 5],
        borders=[1], area_thresh=10000, land="gray", water="skyblue"
    )
    fig.basemap(
        frame=[
            'a4f3g6',
            "+t\"Eventos Sismológicos pós-tratamento por Profundidade (km)\""
        ]
    )
    fig.plot(
        x=catalog[catalog['Depth/km'] <= 1].Longitude,
        y=catalog[catalog['Depth/km'] <= 1].Latitude,
        style="c0.1c", fill="blue",
        label=f"Profundidade < 1 km ({nb_ev_blue})"
    )
    fig.plot(
        x=catalog[(catalog['Depth/km'] > 1) & (catalog['Depth/km'] <= 5)].Longitude,
        y=catalog[(catalog['Depth/km'] > 1) & (catalog['Depth/km'] <= 5)].Latitude,
        style="c0.2c", fill="green", label=f"Profundidade 1 - 5 km ({nb_ev_1})")
    fig.plot(
        x=catalog[(catalog['Depth/km'] > 5) & (catalog['Depth/km'] <= 25)].Longitude,
        y=catalog[(catalog['Depth/km'] > 5) & (catalog['Depth/km'] <= 25)].Latitude,
        style="c0.2c", fill="orange", label=f"Profundidade 5 - 25 km ({nb_ev_5})"
    )
    fig.plot(
        x=catalog[(catalog['Depth/km'] > 25) & (catalog['Depth/km'] <= 50)].Longitude,
        y=catalog[(catalog['Depth/km'] > 25) & (catalog['Depth/km'] <= 50)].Latitude,
        style="c0.2c", fill="red", label=f"Profundidade 25 - 50 km ({nb_ev_25})"
    )
    fig.legend(position="JBR+jBR+o0.5c/0.5c", box="+gwhite+p1p,black")
    fig.text(x=-52, y=8, text="Eventos Sismológicos pós-tratamento por Profundidade (km)", font="16p,Helvetica-Bold")
    fig.savefig('arquivos/figuras/pre_process/mapas/mapa_eventos_clean.png')
    fig.show()


# ----------------------------  MAIN  -----------------------------------------
def main(args=args):
    if args.catalogo:
        catalog = pd.read_csv(f'arquivos/catalogo/{args.catalogo}', sep='|')
        catalog.rename(columns={'#EventID': 'EventID'}, inplace=True)
        catalog = profundidade_catalogo(catalog)
        catalog = order_catalog(catalog, args.ascending)
        catalog = brasil_catalogo(catalog)
        catalog.to_csv(
            f"arquivos/catalogo/{args.catalogo.split('.')[0]}_treated.csv",
            index=False
        )
        if args.plot:
            catalog = pd.read_csv(
                f'arquivos/catalogo/{args.catalogo}',
                sep='|'
            )
            catalog.rename(columns={'#EventID': 'EventID'}, inplace=True)
            plot_prof_as_red(catalog)

            catalogo_treated = pd.read_csv(
                f'arquivos/catalogo/{args.catalogo.split(".")[0]}_treated.csv'
            )
            plot_cleaned_catalog_pygmt(catalogo_treated)

    if args.eventos:
        eventos = pd.read_csv(f'arquivos/eventos/{args.eventos}', sep=',')
        if args.plot:
            eventos = pd.read_csv(
                f'arquivos/eventos/{args.eventos}',
                sep=','
            )
            plot_cleaned_catalog_pygmt(eventos)

    else:
        print('Nenhum argumento foi passado')


if __name__ == '__main__':
    catalog = main()
