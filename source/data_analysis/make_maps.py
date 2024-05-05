# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/source/data_analysis/make_maps.py

# ----------------------------  DESCRIPTION  -----------------------------------
# Script para gerar mapas com os dados das predições
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.2
# Data: 2024-05-04
# Modificação mais recente: 2024-05-04

# ----------------------------  IMPORTS   -------------------------------------
import pygmt
import pandas as pd

# ----------------------------  FUNCTIONS  -------------------------------------
def plot_map(data, output_file):
    """
    Função para plotar um mapa com os dados de predição
    """
    fig = pygmt.Figure()
    fig.basemap(region=[-180, 180, -90, 90], projection="W15c", frame=True)
    # Add Brazil coastlines
    fig.coast(
        shorelines=True,
        land="black",
        water="skyblue",
        borders=1,
        resolution="f",
    )

    fig.plot(
        x=data["Longitude"],
        y=data["Latitude"],
        style="c0.2c",
    )
    fig.colorbar(frame=["x+lLongitude", "y+lLatitude"])
    fig.savefig(output_file)


# ----------------------------  MAIN  -------------------------------------
def main():
    data = pd.read_csv("files/output/no_commercial/df_nc_pos.csv")
    plot_map(data, "mapa.png")

    return data


if __name__ == "__main__":
    data = main()
