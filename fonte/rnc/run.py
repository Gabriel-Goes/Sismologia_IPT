#! /usr/bin/env python3
# coding: utf-8

import argparse

import numpy as np

from cnn.prediction import discrim
from cnn.data_process import spectro_extract


def read_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser()

    parser.add_argument('--model',
                        type=str, default='ClassificadorSismologico/source/discrimination_eq_q/model/model_2021354T1554.h5',
                        help="Model file directory.")

    parser.add_argument('--mseed_dir',
                        type=str, default='ClassificadorSismologico/files/mseed',
                        help="Input mseed file directory.")

    parser.add_argument('--spectro_dir',
                        type=str, default='ClassificadorSismologico/files/spectro',
                        help='Output spectrogram file directory.')

    parser.add_argument('--predcsv',
                        required=True,
                        help="Input csv file directory")

    parser.add_argument('--output_dir',
                        type=str, default='ClassificadorSismologico/files/output',
                        help='Output directory')

    parser.add_argument('--valid',
                        action="store_true",
                        help=' if the option "valid" is specified the validation mode will be applied. Csv input must have two columns (time, label_cat)')

    args = parser.parse_args()
    return args


def main(args: argparse.Namespace):
    events = np.genfromtxt(
        f'ClassificadorSismologico/files/predcsv/{args.predcsv}',
        delimiter=',',
        skip_header=1,
        dtype=str
    )
    spectro_extract(
        mseed_dir=args.mseed_dir,
        spectro_dir=args.spectro_dir,
        events=events
    )
    discrim(
        model=args.model,
        spectro_dir=args.spectro_dir,
        output_dir=f'ClassificadorSismologico/files/output/{args.output_dir}',
        events=events,
        valid=args.valid
    )

    return


if __name__ == '__main__':
    args = read_args()
    main(args)
