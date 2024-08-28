# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/analise_dados/pre_processa.py

# ---------------------------  DESCRIPTION  -----------------------------------
# Script para tratar dados anterior a classificação.
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.2.2
# Data: 2024-02-27
# Modificação mais recente: 2024-08-08
# Descrição: Este script será chamado antes da aquisição dos dados e apóes a
# aquisição dos dados. Ele será responsável por tratar os dados do catálogo.csv
# e dos eventos.csv. O catalogo.csv será filtrado criando um
# catalogo_treated.csv que será iterado pela fluxo_eventos.py

# ----------------------------  IMPORTS   -------------------------------------
import pandas as pd
import shapely.geometry
import geopandas as gpd
import pygmt
import random
import matplotlib.pyplot as plt
import numpy as np
import argparse
import matplotlib
# import locale
# import warnings

from obspy.core import UTCDateTime

matplotlib.use('Agg')
# warnings.filterwarnings("ignore")
# # Configurações do Matplotlib para usar pgf
# locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')


###############################################################################
# ----------------------------  ARGUMENTS  ------------------------------------
parser = argparse.ArgumentParser(description='Pre processamento dos dados')
parser.add_argument(
    '--eventos', '-e', default='eventos.csv',
    type=str, help='Nome do arquivo csv dos eventos'
)
parser.add_argument(
    '--csv', '-c', default='Catalog.csv',
    type=str, help='Nome do arquivo csv do catalogo'
)
parser.add_argument(
    # Default TRUE
    '--ascending', '-a', action='store_false', default=True,
    help='Ordenar catalogo por data crescente'
)
parser.add_argument(
    '--map', '-m', default=True, type=bool,
    help='Plotar distribuição do catalogo'
)
parser.add_argument(
    '--test', '-t', default=False, type=bool,
    help='Testar a função'
)
args = parser.parse_args()


# ----------------------------  FUNCTIONS  ------------------------------------
def read_catalogo(csv: str, sep: str = '|') -> pd.DataFrame:
    catalog_raw = pd.read_csv(f'arquivos/catalogo/{csv}', sep=sep)
    catalog_raw.rename(columns={'#EventID': 'EventID'}, inplace=True)

    return catalog_raw


def data_catalogo(
        catalogo: pd.DataFrame,
        ascending: bool = False,
        data: str = '2010'
) -> pd.DataFrame:
    catalogo['Time'] = pd.to_datetime(catalogo['Time'])
    catalogo['Hora'] = catalogo['Time'].apply(lambda x: x.hour)
    catalogo['Time'] = pd.to_datetime(catalogo['Time'])
    catalogo.sort_values(by='Time', ascending=ascending, inplace=True)
    catalogo = catalogo[catalogo['Time'] > data + '-01-01']
    print(catalogo['Time'].min())

    return catalogo


def brasil_catalogo(catalogo: pd.DataFrame) -> pd.DataFrame:
    df = catalogo.copy()
    df['geometry'] = df.apply(
        lambda x: shapely.geometry.Point(x['Longitude'], x['Latitude']), axis=1
    )
    df = gpd.GeoDataFrame(df, geometry='geometry')
    world = gpd.read_file('arquivos/figuras/mapas/shp/ne_110m_admin_0_countries.shp')
    brasil = world[world['SOVEREIGNT'] == 'Brazil']
    brasil = brasil.to_crs(epsg=32723)
    brasil_buffer = brasil.buffer(400000)
    brasil_buffer = brasil_buffer.to_crs(epsg=4326)
    catalog_br = df[df.within(brasil_buffer.unary_union)]

    return catalog_br


def filter_pred_com(pred: pd.DataFrame) -> pd.DataFrame:
    pred = pred.reset_index()
    pred['Hora'] = pred['Event'].apply(lambda x: UTCDateTime(x).hour)
    pred_com = pred[(pred['Hora'] >= 11) & (pred['Hora'] < 22)]
    pred_nc = pred[(pred['Hora'] < 11) | (pred['Hora'] >= 22)]
    pred_com = pred_com.drop(columns=['Hora'])
    pred_nc = pred_nc.drop(columns=['Hora'])
    pred_com.to_csv('arquivos/resultados/test_comm.csv', index=False)
    pred_nc.to_csv('arquivos/resultados/test_ncomm.csv', index=False)

    return pred, pred_com, pred_nc


def check_ev_id():
    old_c = pd.read_csv('arquivos/catalogo/Catalog.csv', sep=';')
    c = pd.read_csv(
        'arquivos/catalogo/catalogo-moho-south-america.csv',
        sep='|'
    )
    oldids = old_c[''].to_list()
    ids = c[''].to_list()
    for i in oldids:
        if i not in ids:
            print(i)


# ----------------------------  PLOT  -----------------------------------------
def plot_distrib_hora(
        catalog: pd.DataFrame, title='completo',
        textwidth=7, scale=1.0, aspect_ratio=6 / 8
) -> None:
    print('')
    print('Plotando distribuição de eventos por hora...')
    data_i = catalog['Time'].min().strftime('%b de %Y')
    data_f = catalog['Time'].max().strftime('%b de %Y')
    counts = catalog['Hora'].value_counts(sort=False).reindex(np.arange(24), fill_value=0)
    print(f' Catálogo {title} com {catalog.shape[0]} eventos')
    print(f' {data_i} à {data_f}')
    density = counts / counts.sum()
    width = textwidth * scale
    height = width * aspect_ratio
    fig, ax = plt.subplots(figsize=(width, height), constrained_layout=True)
    colors = ['#1f77b4' if (11 <= hour < 22) else '#ff7f0e' for hour in counts.index]
    bars = ax.bar(
        counts.index,
        density,
        color=colors, alpha=0.7, width=0.8, edgecolor='black'
    )
    yval_max = 0
    for b, l in zip(bars, counts):
        yval = b.get_height()
        yval_max = yval if yval > yval_max else yval_max
        ax.text(
            b.get_x() + b.get_width() / 2,
            yval + 0.002,
            int(l),
            ha='center', va='bottom', fontsize=8
        )
    plt.line = ax.axhline(
        y=0.04166, color='red', linewidth=0.4, alpha=0.6, linestyle='--')
    ax.legend(
        [bars[0], bars[12]],
        ['Horário Não Comercial', 'Horário Comercial'],
        loc='best',
        fontsize=8, fancybox=False,
        edgecolor="black").get_frame().set_linewidth(0.5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
    ax.set_xticks(range(0, 24))
    ax.set_yticks(np.arange(0, 0.08, 0.01))
    ax.set_xticklabels(range(0, 24), fontsize=8)
    ax.set_yticklabels(
        ['{:,.0%}'.format(x) for x in ax.get_yticks()],
        fontsize=8
    )
    # ax.set_yticklabels(['{:,.0%}'.format(x) for x in ax.get_yticks()], fontsize=8)
    ax.grid(axis='y', linestyle='--', linewidth=0.7)
    fig.suptitle('Distribuição de Eventos por Hora', fontsize=10)
    ax.set_title(f'Catálogo {title} com {catalog.shape[0]} eventos de {data_i} à {data_f}', fontsize=8)
    ax.set_xlabel('Hora (UTC)', fontsize=9)
    ax.set_ylabel('Frequência (%)', fontsize=9)
    ax.set_ylim(0, 0.07)
#     plt.savefig(f'arquivos/figuras/pre_processa/hist_hora_{title}.pgf', dpi=300)
    plt.savefig(f'arquivos/figuras/pre_processa/hist_hora_{title}.png', dpi=300)
    plt.close()


def profundidade_catalogo(
        catalogo: pd.DataFrame,
        title='completo',
        textwidth=7, scale=1.0, aspect_ratio=6 / 8
) -> None:
    width = textwidth * scale
    height = width * aspect_ratio
    plt.figure(figsize=(width, height), constrained_layout=True)
    plt.yscale('log')
    n, bins, patches = plt.hist(
        catalogo['Depth/km'],
        bins=100,
        color='#1f77b4',
        edgecolor='black',
        alpha=0.7,
        density=False,
    )
    plt.suptitle('Distribuição de Profundidade')
    plt.title(f'Catálogo {title} com {catalogo.shape[0]} eventos')
    plt.xlabel('Profundidade (km)')
    plt.ylabel('Frequência absoluta (log)')
    plt.xticks(np.arange(0, 700, 50))
    plt.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'arquivos/figuras/pre_processa/hist_profundidade_{title}.png')
#     # plt.savefig(f'arquivos/figuras/pre_processa/hist_profundidade_{title}.pgf')
    # plt.show()


def plot_out_of_brasil_as_red(catalog: pd.DataFrame) -> None:
    catalog.drop_duplicates(subset='', inplace=True)
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
    plt.savefig('arquivos/figures/mapas/completo_catalog_mapa.png')
    plt.close()
    # plt.show()


def plot_prof_as_red(catalog: pd.DataFrame, title='completo') -> None:
    catalog.drop_duplicates(subset='EventID', inplace=True)
    catalog = gpd.GeoDataFrame(
        catalog,
        geometry=gpd.points_from_xy(catalog.Longitude, catalog.Latitude)
    )
    capitals = pd.DataFrame({
        "city": [
            "Brasília",
            "Salvador", "Fortaleza", "Manaus", "Recife",
        ],
        "latitude": [
            -15.7801, -12.9714,
            -3.71722, -3.119028, -8.04756
        ],
        "longitude": [
            -47.9292, -38.5014,
            -38.5434, -60.021731, -34.87664
        ]
    })
    region = (
        catalog['Longitude'].min() - 0.1,
        catalog['Longitude'].max() + 1.25,
        catalog['Latitude'].min() - 0.1,
        catalog['Latitude'].max() + 0.1
    )
    catalog.crs = 'EPSG:4326'
    brasil = gpd.read_file('arquivos/figuras/mapas/macrorregioesBrasil.json')
    brasil.to_crs(epsg=4326, inplace=True)
    brasil = brasil.geometry.unary_union
    fig = pygmt.Figure()
    pygmt.makecpt(
        cmap="jet",
        series=[catalog['Depth/km'].min(),
                catalog['Depth/km'].max()]
    )
    fig.coast(
        shorelines='1/0.5p',
        projection="M10i",
        region=region,
        borders=[1],
        area_thresh=10000,
        land="gray",
        water="skyblue"
    )
    if title == 'completo':
        fig.basemap(
            frame=[
                'a4f3g6',
                "+tEventos sismológicos pré-tratamento por profundidade (km)"
            ]
        )
    else:
        fig.basemap(
            frame=[
                'a4f3g6',
                "+tEventos sismológicos pós-tratamento por profundidade (km)"
            ]
        )
    fig.plot(
        x=catalog['Longitude'],
        y=catalog['Latitude'],
        size=0.03 * (catalog['Magnitude']),
        fill=catalog['Depth/km'],
        cmap=True,
        style="cc",
        pen="black"
    )
    fig.plot(
        x=capitals['longitude'],
        y=capitals['latitude'],
        style="c0.1", fill="white", pen="black",
        label="Capitais"
    )
    fig.plot(
        x=capitals['longitude'],
        y=capitals['latitude'],
        style="c0.075c", fill="black",
        label="Capitais"
    )
    for index, row in capitals.iterrows():
        fig.text(
            x=row['longitude'],
            y=row['latitude'],
            text=row['city'],
            font="10p,Helvetica,black",
            justify="TL",  # Ajuste de acordo com a necessidade
            offset="0.1c/0.1c"
        )
    fig.legend(position="JBR+jBR+o3c/0c", box="+gwhite+p1p,black")
    fig.basemap(rose="jTL+w2c+o0.5c/0.5c+f")
    fig.colorbar(
        frame=["x+lProfundidade", "y+lkm"],
        box="+gwhite+p1p,black",
        position="JMR+o-2c/-9c+w5c/0.25c"
    )
    try:
        print('Salvando mapa...')
        fig.savefig(f'arquivos/figuras/mapas/mapa_eventos_{title}.png')
    except pygmt.clib.GMTCLibError as e:
        print(f"Erro ao salvar como PNG: {e}")
    # fig.show()


def plot_by_macrorregioes(
        catalog: pd.DataFrame,
        title: str = 'completo',
        attribute: str = 'Depth/km',
        textwidth=7,
        scale=1.0,
        aspect_ratio=6 / 8,
        bins=10
) -> None:
    width = textwidth * scale
    height = width * aspect_ratio
    macro_br = gpd.read_file('arquivos/figuras/mapas/macrorregioesBrasil.json')
    macro_br = macro_br.to_crs(epsg=4326)
    regions = list(macro_br['nome']) + ['Exterior']
    num_regions = len(regions)
    cols = 3
    rows = (num_regions + cols - 1) // cols
    fig, axes = plt.subplots(
        rows, cols,
        figsize=(width, height),
        constrained_layout=True
    )
    axes = axes.flatten()
    all_geometries = macro_br['geometry'].unary_union
    for i, regiao in enumerate(regions):
        ax = axes[i]
        ax.set_title(regiao, fontsize=10)
        ax.set_yscale('log')
        ax.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)
        ax.set_xlabel('Profundidade (km)', fontsize=8)
        ax.set_ylabel('Frequência', fontsize=8)
        if regiao != 'Exterior':
            data = catalog[attribute][catalog['geometry'].within(
                macro_br.loc[macro_br['nome'] == regiao, 'geometry'].values[0]
            )]
        else:
            data = catalog[attribute][~catalog['geometry'].within(
                all_geometries
            )]
        counts, bin_edges, _ = ax.hist(
            data,
            bins=bins,
            color='#1f77b4',
            edgecolor='black',
            alpha=0.7,
            density=False
        )
        for j in range(len(bin_edges) - 1):
            bin_value = counts[j] / catalog.shape[0] * 100
            ax.text(
                (bin_edges[j] + bin_edges[j + 1]) / 2,
                counts[j],
                f'{bin_value:.2f}%',
                ha='center',
                va='bottom',
                fontsize=6,
            )
    for ax in axes[num_regions:]:
        fig.delaxes(ax)
    fig.suptitle('Distribuição de Profundidade por Macrorregiões', fontsize=12)
    plt.subplots_adjust(top=0.92)
    # plt.show()


# ----------------------------  MAIN  -----------------------------------------
def main(args=args):
    print(f'Argumentos recebidos:\n {args.eventos}\n {args.csv}\n {args.map}\n {args.test}')
    if args.csv:
        catalogo_r = read_catalogo(args.csv, sep='|')
        if args.test is True:
            print('Testando...')
            random.seed(42)
            catalogo_r = catalogo_r.sample(catalogo_r.shape[0] // 3)
        catalogo = data_catalogo(catalogo_r)
        catalogo = brasil_catalogo(catalogo)
        catalogo['Author'] = catalogo['Author'].str.upper()
        catalogo['Author'] = catalogo['Author'].str.strip()
        catalogo['Author'] = catalogo['Author'].replace(
            {
                'BRUNO@LAB88': 'BRUNO',
                'BBCOLLACO': 'BRUNO',
                'BRUNO@MAVERICK.LOCAL': 'BRUNO',
                'MARCELO': 'MASSUMPCAO',
                'JROBERTO@VITORIA': 'JROBERTO',
            }
        )
        plot_distrib_hora(catalogo, title='filtrado')
        plot_distrib_hora(catalogo_r)
        profundidade_catalogo(catalogo_r)
        profundidade_catalogo(catalogo, title='filtrado')
        c_filtrado = f"arquivos/catalogo/{args.csv.split('.')[0]}_filtrado.csv"
        catalogo.to_csv(
            c_filtrado,
            sep='|',
            index=False
        )
        if args.map:
            print('Plotando mapa...')
            plot_prof_as_red(catalogo_r)
            plot_prof_as_red(catalogo, 'filtrado')

    elif args.eventos:
        eventos = pd.read_csv(f'arquivos/eventos/{args.eventos}', sep=',')
        if args.map:
            plot_prof_as_red(eventos)

    else:
        print('Nenhum argumento foi passado')
        return None

    plt.close()
    return catalogo


if __name__ == '__main__':
    catalogo = main()
