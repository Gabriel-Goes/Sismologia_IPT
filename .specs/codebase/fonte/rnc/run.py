#! /usr/bin/env python3
# coding: utf-8

import argparse
import pandas as pd
from prediction import discrim
from data_process import spectro_extract

cs = 'ClassificadorSismologico/'
model = 'fonte/rnc/model/model_2021354T1554.h5'
mseed = 'arquivos/mseed'
spectro = 'arquivos/espectros'
output = 'arquivos/resultados'


def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--model',
                        type=str, default=model,
                        help="Model file path.")

    parser.add_argument('--mseed_dir',
                        type=str, default=mseed,
                        help="Input mseed file directory.")

    parser.add_argument('--spectro_dir',
                        type=str, default=spectro,
                        help='Output spectrogram file directory.')

    parser.add_argument('--output_dir',
                        type=str, default=output,
                        help='Output directory')

    parser.add_argument('--valid',
                        action="store_true",
                        help=' if the option "valid" is specified the \
                        validation mode will be applied. Csv input must have \
                        two columns (time, label_cat)')
    parser.add_argument('--test-limit',
                        type=int, default=0,
                        help='Limita a quantidade de eventos unicos em modo de teste.')

    args = parser.parse_args()
    return args


def main(args: argparse.Namespace):
    eventos = pd.read_csv(
        'arquivos/eventos/eventos.csv'
    )
    if args.test_limit and args.test_limit > 0:
        if 'Event' in eventos.columns:
            unique_events = eventos['Event'].dropna().drop_duplicates()
            sample_n = min(args.test_limit, len(unique_events))
            sampled_events = unique_events.sample(n=sample_n, random_state=42)
            eventos = eventos[eventos['Event'].isin(sampled_events)]
            print(f' --> Modo de teste RNC: {sample_n} eventos unicos selecionados ({len(eventos)} picks).')
        else:
            sample_n = min(args.test_limit, len(eventos))
            eventos = eventos.sample(n=sample_n, random_state=42)
            print(f' --> Modo de teste RNC: {sample_n} linhas selecionadas.')
    eventos = spectro_extract(
        mseed_dir=args.mseed_dir,
        spectro_dir=args.spectro_dir,
        eventos=eventos
    )

    eventos_error = eventos.loc[eventos['Error'].apply(len) > 0]
    eventos_error.to_csv('arquivos/resultados/erros.csv', index=False)
    eventos_clean = eventos.loc[eventos['Error'].apply(len) == 0]
    eventos_clean.to_csv('arquivos/resultados/pre_processado.csv')
    eventos_clean = pd.read_csv('arquivos/resultados/pre_processado.csv')

    discrim(
        model=args.model,
        spectro_dir=args.spectro_dir,
        output_dir=args.output_dir,
        eventos=eventos_clean,
    )
    return


if __name__ == '__main__':
    args = read_args()
    main(args)
