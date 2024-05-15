# coding: utf-8

import glob
import os
import csv
import numpy as np
import pandas as pd
from numpy import moveaxis
import tensorflow as tf


def discrim(
        model: str,
        spectro_dir: str,
        output_dir: str,
        events: list,
        valid: bool) -> None:
    """
    model_dir: Absolute path to the input trained model.
    spectro_dir: Absolute path to the input spectrograms.
    output_dir: Absolute path where to save to output files.
    events: List of events to predict.
    """
    model = tf.keras.models.load_model(model)
    print(f'Number of events: {len(events)}')
    for i, e in events.iterrows():
        print(e.name)
        if valid:
            event = e.name
            label = e['Label']
            print(f' - Event: {event}\n - Label: {label}')
        else:
            event = e.name
        pred_nat = pred_ant = 0
        list_spect = glob.glob(f'{spectro_dir}/{event}/*')
        print('*****************')
        print(f'EVENT {events.index.get_loc(event)+1} / {events.shape[0]}')
        print(f'Number of picks: {len(list_spect)}')
        n_pck = 0
        for spect in list_spect:
            n_pck += 1
            pck = (spect.split('/')[-1]).split('.npy')[0]
            net = (pck.split('_')[0])
            sta = (pck.split('_')[1])
            spect_file = np.load(spect, allow_pickle=True)
            spect_file = [np.array(spect_file)]
            print(f' - Espectro: {spect}')
            print(f' - #Pick {n_pck} / {len(list_spect)}')
            print(f' - Pick: {pck}')

            break

            x = moveaxis(spect_file, 1, 3)
            model_output = model.predict(
                x,
                use_multiprocessing=True,
                verbose=True
            ).round(9)
            pred = np.argmax(model_output, axis=1)
            print(f' - Model output: {model_output}')
            print(f' - Prediction: {model_output[0]}')
            print(f' - Pred: {pred}')
            print(f' - Pred: {pred[0]}')

            if pred == 0:
                pred_final = 'Natural'
            if pred == 1:
                pred_final = 'Anthropogenic'

            if valid:
                [
                    pck,
                    model_output[0][0],
                    pred[0],
                    pred_final,
                    label,
                ]
            else:
                [
                    pck,
                    model_output[0][0],
                    pred[0],
                    pred_final,
                ]

            pred_nat += model_output[0][0]
            pred_ant += model_output[0][1]
            print(f' - Pred nat: {pred_nat}')
            print(f' - Pred ant: {pred_ant}')
            print('*****************')

        break
        pred_total = [pred_nat, pred_ant]
        try:
            pred_total = [
                (float(i) / sum(pred_total)).round(9) for i in pred_total
            ]
            print(f' - Pred total: {pred_total}')
        except ZeroDivisionError:
            print(f'Erro Evento: {event}')
        pred_event = np.argmax(pred_total)
        if pred_event == 0:
            pred_final = 'Natural'
        if pred_event == 1:
            pred_final = 'Anthropogenic'

        if valid:
            df.writerow([
                event,
                label,
                pred_total[0],
                pred_total[1],
                pred_event,
                pred_final,
            ])
        else:
            df.writerow([
                event,
                pred_total[0],
                pred_total[1],
                pred_event,
                pred_final,
            ])

        df.to_csv(f'{output_dir}/{filename_csv}', index=True)


# ---------------------------- MAIN -------------------------------------------
def main():
    model = 'source/cnn/model/model_2021354T1554.h5'

    spectro_dir = 'files/spectro'

    output_dir = 'files/output'

    # load events with 'Event' as  index
    events = pd.read_csv(
        'files/predcsv/pred_no_commercial.csv',
        delimiter=',',
        index_col='Event'
    )

    df = discrim(
        model=model,
        spectro_dir=spectro_dir,
        output_dir=output_dir,
        events=events.head(5),
        valid=True
    )
    return events
