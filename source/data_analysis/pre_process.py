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
def gerar_predcsv():
    # Criar Lista de Eventos para Predição
    csv_events = './files/events/events.csv'
    df_events = pd.read_csv(csv_events, sep=',')

    # Se IDs iguais possuem Cat diferentes adicionar em uma lista de erros
    erros = []
    for id in df_events['ID'].unique():
        if len(df_events[df_events['ID'] == id]['Cat'].unique()) > 1:
            erros.append(id)

    # Remover IDs com Cat diferentes
    df_events_clean = df_events[~df_events['ID'].isin(erros)]
    df_pred = df_events_clean[['Event', 'Cat']]

    # Transforma 'earthquake' em 0 e qualquer outra coisa em 0
    df_pred['Cat'] = df_pred['Cat'].apply(lambda x: 0 if x == 'earthquake' else 1)

    # rename columns
    df_pred.columns = ['ID', 'Label']

    # Remove os IDs duplicados
    df_pred = df_pred.drop_duplicates()

    # Salvar o DataFrame em um arquivo CSV
    df_pred.to_csv('./files/predcsv/pred.csv', index=False)

    df_erros = pd.DataFrame(erros, columns=['ID'])
    df_erros.to_csv('./files/predcsv/erros.csv', index=False)


# Função para filtrar eventos fora do horário comercial
def filter_pred_com(csv: str) -> pd.DataFrame:
    df = pd.read_csv(csv)
    df['Hora'] = df['ID'].apply(lambda x: UTCDateTime(x).hour)
    df_com = df[(df['Hora'] >= 11) & (df['Hora'] < 22)]
    df_nc = df[(df['Hora'] < 11) | (df['Hora'] >= 22)]
    df_com = df_com.drop(columns=['Hora'])
    df_nc = df_nc.drop(columns=['Hora'])
    df_com.to_csv('files/predcsv/pred_commercial.csv', index=False)
    df_nc.to_csv('files/predcsv/pred_no_commercial.csv', index=False)

    return df, df_com, df_nc


# ----------------------------  PLOT  -----------------------------------------
def hist_hora(
        df: pd.DataFrame,
        df_com: pd.DataFrame,
        df_nc: pd.DataFrame) -> [pd.DataFrame]:
    counts = df['Hora'].value_counts(
        sort=False
    ).reindex(np.arange(24), fill_value=0)
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
    # plt.show()
    df_com.to_csv('files/predcsv/pred_commercial.csv', index=False)
    df_nc.to_csv('files/predcsv/pred_no_commercial.csv', index=False)
    return df_com, df_nc


# ----------------------------  MAIN  -----------------------------------------
def main():
    gerar_predcsv()
    df, df_com, df_nc = filter_pred_com('files/predcsv/pred.csv')
    df, df_com, df_nc = hist_hora(df, df_com, df_nc)


if __name__ == '__main__':
    df, df_com, df_nc = main()
