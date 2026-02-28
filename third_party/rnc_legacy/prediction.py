# coding: utf-8

import numpy as np
from numpy import moveaxis
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
import pandas as pd


def discrim(
        model: str,
        spectro_dir: str,
        output_dir: str,
        eventos: pd.DataFrame) -> None:
    """
    Event class prediction.

    :param model_dir: Absolute path to the input trained model.
    :param spectro_dir: Absolute path to the input spectrograms.
    :param output_dir: Absolute path where to save to output files.
    """

    try:
        eventos.set_index(['Event', 'Station'], inplace=True)
        eventos.sort_index(inplace=True)
    except KeyError:
        pass

    model = tf.keras.models.load_model(model)
    optimizer = Adam(learning_rate=0.001)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    n_ev = eventos.groupby('Event').size().shape[0]
    print(f'Number of events: {n_ev}')
    for i, (ev_index, evento) in enumerate(eventos.groupby('Event'), 1):
        n_pcks = evento.shape[0]
        print('*****************')
        print(f'EVENT {i} / {n_ev}')
        print(f'Number of Picks: {n_pcks}')
        pred_nat = 0
        pred_ant = 0

        for j, (st_index, pick) in enumerate(evento.groupby('Station'), 1):
            print(f'Pick {j} / {n_pcks}', end="\r")
            mseed = pick['Path'].values[0].split('/')[-1]
            npy = mseed.replace('.mseed', '.npy')
            spect_path = f'{spectro_dir}/{ev_index}/{npy}'
            try:
                spectre_file = np.load(spect_path, allow_pickle=True)
            except FileNotFoundError:
                print(f'File not found: {spect_path}')
                eventos.loc[(ev_index, st_index)]['Error'].append(
                    f'File not found: {spect_path}'
                )
                continue
            spect = [np.array(spectre_file)]

            x = moveaxis(spect, 1, 3)

            model_output = model.predict(x).round(3)
            pred_pick = np.argmax(model_output, axis=1)

            if pred_pick == 0:
                pred_final = 'Natural'
            if pred_pick == 1:
                pred_final = 'Anthropogenic'

            eventos.loc[(ev_index, st_index), 'Pick Pred'] = pred_pick[0]
            eventos.loc[(ev_index, st_index), 'Pick Prob_Nat'] = model_output[0][0]
            eventos.loc[(ev_index, st_index), 'Pick Prob_Ant'] = model_output[0][1]
            eventos.loc[(ev_index, st_index), 'Pick Pred_final'] = pred_final

            pred_nat += model_output[0][0]
            pred_ant += model_output[0][1]

        pred_total = [pred_nat, pred_ant]
        try:
            pred_total = [
                (float(k) / sum(pred_total)).round(3) for k in pred_total
            ]
        except ZeroDivisionError:
            eventos.loc[(ev_index, st_index)]['Error'].append(
                f'ZeroDivisionError {pred_total}'
            )
            print(f'Erro Evento: {ev_index} {pred_total}')
            continue

        pred_event = np.argmax(pred_total)

        if pred_event == 0:
            pred_final = 'Natural'
        if pred_event == 1:
            pred_final = 'Anthropogenic'

        eventos.loc[(ev_index,), 'Event Pred'] = pred_event
        eventos.loc[(ev_index,), 'Event Prob_Nat'] = pred_total[0]
        eventos.loc[(ev_index,), 'Event Prob_Ant'] = pred_total[1]
        eventos.loc[(ev_index,), 'Event Pred_final'] = pred_final

    eventos.to_csv(f'{output_dir}/predito.csv')
