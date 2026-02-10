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
import numpy as np
import geopandas as gpd
import os
import tempfile


# ----------------------------  FUNCTIONS   --------------------------------- #
def plot_pred_map(data, filename):
    # Definir região do mapa
    region = [
        data['Longitude'].min() - 1, data['Longitude'].max() + 1,
        data['Latitude'].min() - 1, data['Latitude'].max() + 1
    ]
    fig = pygmt.Figure()
    pygmt.makecpt(
        cmap="polar", series=[data['Event Prob_Nat'].min(), data['Event Prob_Nat'].max()]
    )
    fig.basemap(region=region, projection='M15c', frame=True)
    fig.coast(land="lightgray", water="skyblue")

    # Adicionar jitter aos dados para evitar sobreposição
    jitter_strength = 0.1  # Ajuste conforme necessário
    data['Longitude_jitter'] = data['Longitude'] + np.random.uniform(-jitter_strength, jitter_strength, size=len(data))
    data['Latitude_jitter'] = data['Latitude'] + np.random.uniform(-jitter_strength, jitter_strength, size=len(data))

    fig.plot(
        x=data['Longitude_jitter'],
        y=data['Latitude_jitter'],
        fill=data['Event Prob_Nat'],
        style='c0.1c',  # Diminuir o tamanho dos pontos
        cmap=True,
        transparency=50  # Adicionar transparência
    )

    # Adicionar título ao mapa
    fig.text(
        x=0.5 * (region[0] + region[1]),
        y=region[3] - 0.5,
        text=f"Mapa de Predições de {data.shape[0]} Eventos rotulados como Naturais",
        font="12p,Helvetica-Bold",
        justify="CM",
    )

    # Adicionar barra de cores
    fig.colorbar(frame=["x+lProbabilidade", "y+lm"])

    # Adicionar seta de norte
    fig.basemap(rose="jTL+w2c+o0.5c/0.5c+f")

    # Salvar e mostrar figura
    fig.savefig(f'arquivos/figuras/mapas/{filename}')
    fig.show()


def plot_macroregions(gdf, data):
    gdf = gdf.to_crs(epsg=4326)
    jitter_strength = 0.01  # Ajuste conforme necessário
    data['Longitude_jitter'] = data['Longitude'] + np.random.uniform(-jitter_strength, jitter_strength, size=len(data))
    data['Latitude_jitter'] = data['Latitude'] + np.random.uniform(-jitter_strength, jitter_strength, size=len(data))

    for idx, row in gdf.iterrows():
        nome_macroregiao = row["nome"]
        fig = pygmt.Figure()
        bounds = row.geometry.bounds
        lon_min, lat_min, lon_max, lat_max = bounds
        if lon_max - lon_min > 360 or lat_max - lat_min > 180:
            raise ValueError("Os limites da região excedem os valores válidos")

        region = [
            max(-180, lon_min - 1), min(180, lon_max + 1),
            max(-90, lat_min - 1), min(90, lat_max + 1)
        ]
        fig.basemap(region=region, projection="M6i", frame=True)
        fig.coast(
            shorelines=True,
            resolution='10m',
            borders=[1],
            water='skyblue'
        )
        fig.plot(
            x=data['Longitude_jitter'],
            y=data['Latitude_jitter'],
            style='c0.1c',
            fill='red',
            transparency=50  # Adicionar transparência
        )

        # Adicionar título ao mapa
        fig.text(
            x=0.5 * (region[0] + region[1]),
            y=region[3] - 0.5,
            text=f"Mapa da Macrorregião {nome_macroregiao}",
            font="12p,Helvetica-Bold",
            justify="CM",
        )

        # Adicionar seta de norte
        fig.basemap(rose="jTL+w2c+o0.5c/0.5c+f")

        # Adicionar legenda
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_legend_file:
            legend_spec = f"""
H 12p,Helvetica Legenda
D 0.2c 1p
N 2
S 0.3c c 0.15c red 0.1p 0.5c Eventos
"""
            temp_legend_file.write(legend_spec)
            temp_legend_file_name = temp_legend_file.name

        legend_width = "10c"
        position = "JBC+o10c/1c+w" + legend_width
        fig.legend(position=position, spec=temp_legend_file_name, box="+gwhite+p1p")

        fig.savefig(f"arquivos/figuras/mapas/{nome_macroregiao}_pred.png")
        fig.show()
        os.remove(temp_legend_file_name)


def main():
    data = pd.read_csv("arquivos/resultados/nc_analisado_final.csv")
    data = data.groupby(['Event']).first()
    plot_pred_map(data, "mapa.png")

    gdf = gpd.read_file("arquivos/figuras/mapas/macrorregioesBrasil.json")
    plot_macroregions(gdf, data)

    return data, gdf


if __name__ == "__main__":
    data = main()
