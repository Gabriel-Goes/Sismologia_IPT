# -*- coding: utf-8 -*-
# Python 3.11.8
# ./Classificador_Sismologico/pyscripts/pre_process.py

# ----------------------------  DESCRIPTION  -----------------------------------
# Script para tratar dados anterior a classificação.
# Autor: Gabriel Góes Rocha de Lima
# Versão: 0.2
# Data: 2024-02-27
# Modificação mais recente: 2024-04-10

# ----------------------------  IMPORTS   -------------------------------------
import pandas as pd
from obspy.core import UTCDateTime

# Plots
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

###############################################################################

# ----------------------------  FUNCTIONS  ------------------------------------


# ---------------------------- HORÁRIO COMERCIAL ---------------------------- #
# Função para filtrar eventos fora do horário comercial
def filter_pred_commercial(csv: str) -> pd.DataFrame:
    df = pd.read_csv(csv)

    # Filtrar eventos fora do horário comercial (11 22)
    df['Hora'] = df['ID'].apply(lambda x: UTCDateTime(x).hour)
    df_commercial = df[(df['Hora'] >= 11) & (df['Hora'] < 22)]
    df_no_commercial = df[(df['Hora'] < 11) | (df['Hora'] >= 22)]

    # Salvar csv
    df_commercial = df_commercial.drop(columns=['Hora'])
    df_no_commercial = df_no_commercial.drop(columns=['Hora'])
    df_commercial.to_csv('files/predcsv/pred_commercial.csv',
                         index=False)
    df_no_commercial.to_csv('files/predcsv/pred_no_commercial.csv',
                            index=False)

    return df, df_commercial, df_no_commercial


# ----------------------------  PLOT  -----------------------------------------
def hist_hora() -> pd.DataFrame:
    # Carregar dados
    csv = 'files/predcsv/pred.csv'
    df, df_commercial, df_no_commercial = filter_pred_commercial(csv)

    counts = df['Hora'].value_counts(sort=False).reindex(
        np.arange(24),
        fill_value=0
    )
    density = counts / counts.sum()
    plt.figure(figsize=(10, 6))
    colors = ['blue' if (11 <= hour < 22) else 'red' for hour in counts.index]
    bars = plt.bar(counts.index, density, color=colors, alpha=0.5, width=0.8)

    for bar, label in zip(bars, counts):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2,
                 yval + 0.001, int(label), ha='center', va='bottom')

    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))

    plt.xticks(range(0, 24))
    plt.grid(axis='y')
    plt.title('Distribuição de eventos sísmicos por hora (UTC)')
    plt.xlabel('Hora (UTC)')
    plt.ylabel('Frequência')
    # Legenda: Commercial e Não-Comercial
    plt.legend(['Horário Comercial', 'Fora do Horário Comercial'],
               loc='upper right')
    # save figure
    plt.savefig('figures/pre_process/plots/histogramas/hist_hora.png')
    plt.show()
    # Salvar csv
    df_commercial.to_csv('files/predcsv/pred_commercial.csv',
                         index=False)
    df_no_commercial.to_csv('files/predcsv/pred_no_commercial.csv',
                            index=False)
    return df_commercial, df_no_commercial


# ----------------------------  MAIN  -----------------------------------------
def main():
    df, df_comm, df_nc = filter_pred_commercial('files/predcsv/pred.csv')
    hist_hora()

    return df, df_comm, df_nc

if __name__ == '__main__':
    df, df_comm, df_nc = main()
