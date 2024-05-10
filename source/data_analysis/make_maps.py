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


# ---------------------------  FUNCTIONS  -------------------------------------
def plot_pred_map(data, filename):
    region = [
        data['Longitude'].min() - 1, data['Longitude'].max() + 1,
        data['Latitude'].min() - 1, data['Latitude'].max() + 1
    ]
    fig = pygmt.Figure()
    pygmt.makecpt(
        cmap="polar", series=[data.prob_nat.min(), data.prob_nat.max()]
    )
    fig.basemap(region=region, projection='M15c', frame=True)
    fig.coast(land="lightgray", water="skyblue")
    fig.plot(
        x=data['Longitude'],
        y=data['Latitude'],
        fill=data.prob_nat,
        style='c0.3c',
        cmap=True,

    )
    fig.show()
    fig.savefig(f'files/figures/maps/{filename}')


# -------------------------------  MAIN  --------------------------------------
def main():
    data = pd.read_csv("files/output/no_commercial/df_nc_pos.csv")
    plot_pred_map(data, "mapa.png")

    return data


if __name__ == "__main__":
    data = main()
