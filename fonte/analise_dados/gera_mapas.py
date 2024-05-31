# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/source/data_analysis/make_maps.py

# ----------------------------  DESCRIPTION  ----------------------------------
# Script para gerar mapas com os dados das predições
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.2
# Data: 2024-05-04
# Modificação mais recente: 2024-05-04

# ----------------------------  IMPORTS   -------------------------------------
import pygmt
import pandas as pd
import geopandas as gpd
from shapely import wkt


# ---------------------------  FUNCTIONS  -------------------------------------
def plot_pred_map(data, filename):
    region = [
        data['Longitude'].min() - 1, data['Longitude'].max() + 1,
        data['Latitude'].min() - 1, data['Latitude'].max() + 1
    ]
    fig = pygmt.Figure()
    pygmt.makecpt(
        cmap="polar", series=[data['Event Prob_Nat'].min(),
                              data['Event Prob_Nat'].max()],
    )
    fig.basemap(region=region, projection='M15c', frame=True)
    fig.coast(land="lightgray", water="skyblue")
    fig.plot(
        x=data['Longitude'],
        y=data['Latitude'],
        fill=data['Event Prob_Nat'],
        style='c0.15c',
        cmap=True,
    )
    fig.colorbar(frame=["x+lProbabilidade", "y+lm"])
    fig.show()
    fig.savefig(f'arquivos/figuras/mapas/{filename}')


def plot_macroregions(gdf, df):
    for idx, row in gdf.iterrows():
        nome_macroregiao = row["nome"]  # Ajuste conforme necessário para o nome da coluna correta

        fig = pygmt.Figure()
        bounds = row.geometry.bounds
        region = [bounds[0] - 1, bounds[2] + 1, bounds[1] - 1, bounds[3] + 1]

        fig.basemap(region=region, projection="M6i", frame=True)
        fig.coast(shorelines=True, resolution='10m', borders=[1], water='skyblue')

        for poly in row.goemetry:
            wkt_polygon = geometry.to_wkt()
        fig.plot(
            data=wkt_polygon,
            pen="1p,black",
            fill="lightgray"
        )



def plot_macroregions(gdf, data):
    gdf = gdf.to_crs(epsg=4326)
    for idx, row in gdf.iterrows():
        nome_macroregiao = row["nome"]  # Ajuste conforme necessário para o nome da coluna correta
        fig = pygmt.Figure()
        bounds = row.geometry.bounds
        lon_min, lat_min, lon_max, lat_max = bounds
        if lon_max - lon_min > 360 or lat_max - lat_min > 180:
            raise ValueError("Os limites da região excedem os valores válidos")

        region = [max(-180, lon_min - 1), min(180, lon_max + 1), max(-90, lat_min - 1), min(90, lat_max + 1)]
        fig.basemap(region=region, projection="M6i", frame=True)
        fig.coast(shorelines=True, resolution='10m', borders=[1], water='skyblue')
        wkt_polygon = row.geometry.to_wkt()
        fig.plot(data=wkt_polygon, pen="1p,black", fill="lightgray")

        fig.savefig(f"arquivos/figuras/mapas/{nome_macroregiao}_pred.png")

# -------------------------------  MAIN  --------------------------------------
def main():
    data = pd.read_csv("arquivos/resultados/304008_analisado.csv")
    data=data.groupby(['Event','Station']).first()
    plot_pred_map(data, "mapa.png")
    gdf = gpd.read_file("arquivos/figuras/mapas/macrorregioesBrasil.json")
    plot_macroregions(gdf, data)

    return data, gdf


if __name__ == "__main__":
    data = main()
