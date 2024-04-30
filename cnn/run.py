#! /usr/bin/env python3
# coding: utf-8

import argparse

import numpy as np

from prediction import discrim
from data_process import spectro_extract

import warnings
warnings.filterwarnings("ignore")


def read_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser()

    parser.add_argument('--model_dir',
                        type=str, default='./model/model_2021354T1554.h5',
                        help="Model file directory.")

    parser.add_argument('--data_dir',
                        type=str, default='./mseed_demo',
                        help="Input mseed file directory.")

    parser.add_argument('--spectro_dir',
                        type=str, default='./spectro_demo',
                        help='Output spectrogram file directory.')

    parser.add_argument('--csv_dir',
                        required=True,
                        help="Input csv file directory")

    parser.add_argument('--output_dir',
                        type=str, default='./output_demo',
                        help='Output directory')

    parser.add_argument('--valid', 
                        action="store_true", 
                        help=' if the option "valid" is specified the validation mode will be applied. Csv input must have two columns (time, label_cat)')

    args = parser.parse_args()
    return args


def main(args: argparse.Namespace):

    events = np.genfromtxt(
            f'{args.csv_dir}', delimiter=',', skip_header=1, dtype=str)

    if events.size == 1:
        events = [events]

    spectro_extract(data_dir=args.data_dir,
                        spectro_dir=args.spectro_dir, events_list=events)
    discrim(model_dir = args.model_dir, spectro_dir=args.spectro_dir,
              output_dir=args.output_dir, event_label=events, valid = args.valid)

    
    return


if __name__ == '__main__':
    args = read_args()
    main(args)
