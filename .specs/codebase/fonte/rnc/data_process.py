# #!/home/ipt/.pyenv/versions/sismologia/bin/python
# coding: utf-8
# Author: Gabriel Góes Rocha de Lima
# CoAuthor: Lucas Schirbel
# Date: 2021-07-01
# Version: 0.1.0

# Description: This script contains the functions used to process the data

# ---------------------------- IMPORT LIBRARIES ----------------------------- #
import os
import matplotlib.mlab as mlab
import numpy as np
import pandas as pd

import obspy as op
from obspy.signal.invsim import cosine_taper
from obspy.signal.trigger import classic_sta_lta
# import matplotlib.pyplot as plt
# from obspy.core import read
# from obspy.signal.trigger import plot_trigger


# ---------------------------- FUNCTION DEFINITIONS ------------------------- #
def stride_windows(x, n, noverlap=None, axis=0):
    if noverlap is None:
        noverlap = 0

    if noverlap >= n:
        raise ValueError('noverlap must be less than n')
    if n < 1:
        raise ValueError('n cannot be less than 1')

    x = np.asarray(x)

    if x.ndim != 1:
        raise ValueError('only 1-dimensional arrays can be used')
    if n == 1 and noverlap == 0:
        if axis == 0:
            return x[np.newaxis]
        else:
            return x[np.newaxis].transpose()
    if n > x.size:
        raise ValueError('n cannot be greater than the length of x')

    # np.lib.stride_tricks.as_strided easily leads to memory corruption for
    # non integer shape and strides, i.e. noverlap or n. See #3845.
    noverlap = int(noverlap)
    n = int(n)

    step = n - noverlap
    if axis == 0:
        shape = (n, (x.shape[-1]-noverlap)//step)
        strides = (x.strides[0], step*x.strides[0])
    else:
        shape = ((x.shape[-1]-noverlap)//step, n)
        strides = (step*x.strides[0], x.strides[0])
    return np.lib.stride_tricks.as_strided(x, shape=shape, strides=strides)


def fft_taper(data: np.ndarray) -> np.ndarray:
    return data * cosine_taper(npts=data.size, p=0.2)


def get_fft(
        trace: op.core.trace.Trace,
        WINDOW_LENGTH: int,
        OVERLAP: float,
        nb_pts: int) -> tuple:
    s_rate = trace.stats.sampling_rate
    nb_pts = int(WINDOW_LENGTH * s_rate)
    nb_overlap = int(OVERLAP * nb_pts)
    window = fft_taper(np.ones(nb_pts, trace.data.dtype))
    result = stride_windows(trace.data, nb_pts, nb_overlap, axis=0)
    result = mlab.detrend(result, mlab.detrend_linear, axis=0)
    result = result * window.reshape((-1, 1))
    numFreqs = nb_pts // 2 + 1
    result = np.fft.fft(result, n=nb_pts, axis=0)[:numFreqs, :]
    freqs = np.fft.fftfreq(nb_pts, 1 / s_rate)[:numFreqs]
    freqs[-1] *= -1
    result = result[1:]
    freqs = freqs[1:]
    result = np.abs(result) / trace.data.size
    result = result.ravel()
    return result, freqs



def decimate_to_100hz(tr):
    tr_hz = tr.stats.sampling_rate
    target_hz = 100
    if tr_hz == target_hz:
        return tr
    elif tr_hz > target_hz:
        factor = tr_hz / target_hz
        while factor % 1 != 0:
            factor = round(factor * 2)
            tr.decimate(2)
        tr.decimate(int(factor))
        print(f' - Warning! Decimated {factor}x to achieve 100 Hz')
    else:
        print(f' - Error! Cannot decimate from {tr_hz} Hz to {target_hz} Hz directly')
        raise ValueError(f'Sampling rate is not compatible for decimation: {tr_hz}')
    return tr


def spectro_extract(
        mseed_dir: str,
        spectro_dir: str,
        eventos: pd.DataFrame) -> None:
    WINDOW_LENGTH = 1
    OVERLAP = (1 - 0.75)
    eventos['Compo'] = [[] for _ in range(len(eventos))]
    eventos['CFT'] = ['' for _ in range(len(eventos))]
    eventos['Error'] = [[] for _ in range(len(eventos))]
    eventos['Warning'] = [[] for _ in range(len(eventos))]
    eventos.reset_index(inplace=True)
    eventos.set_index(['Event', 'Station'], inplace=True)
    eventos.sort_index(inplace=True)

    def append_cell(idx, col, value):
        current = eventos.at[idx, col]
        if isinstance(current, list):
            bucket = current
        elif current in ('', None):
            bucket = []
        else:
            bucket = [current]
        bucket.append(value)
        eventos.at[idx, col] = bucket

    n_ev = eventos.groupby(level=0).size().shape[0]
    print(f'Number of events: {n_ev}')

    for i, (ev_index, evento) in enumerate(eventos.groupby(level=0), start=1):
        print('*****************')
        print(f'EVENT: {ev_index} ({i} / {n_ev})')
        print(f' - Number of picks: {evento.shape[0]}')

        for j, (pk_index, pick) in enumerate(evento.groupby(level=1), start=1):
            print(f'PICK: {pk_index} ({j} / {evento.shape[0]})')
            if pick.shape[0] != 1:
                err = f' - Error! pick.shape[0] != 1 ({pick.shape[0]})'
                append_cell((ev_index, pk_index), 'Error', err)
                print(err)
                continue
            p_path = pick.Path.values[0]
            try:
                st = op.read(f'{mseed_dir}/{p_path}', dtype=float)
            except Exception as e:
                err = f' - Error! read mseed ({p_path}): {e}'
                append_cell((ev_index, pk_index), 'Error', err)
                print(err)
                continue

            compo = [tr.stats.component for tr in st]
            if len(compo) != 3:
                err = f' - Error! len(compo) != 3 ({compo})'
                append_cell((ev_index, pk_index), 'Error', err)
                print(err)
                continue

            for k, tr in enumerate(st):
                try:
                    st[k] = decimate_to_100hz(tr)
                except ValueError as e:
                    print(e)
                    continue

            st.detrend('demean')
            st.taper(0.05)
            st = st.filter('highpass', freq=2, corners=4, zerophase=True)

            cft_max = 0
            for tr in st:
                cft = classic_sta_lta(
                    tr.data,
                    int(1 * tr.stats.sampling_rate),
                    int(5 * tr.stats.sampling_rate)
                )
                cft_max = cft.max() if cft.max() > cft_max else cft_max
            eventos.loc[(ev_index, pk_index), 'CFT'] = cft_max
            if cft_max < 1.5:
                append_cell((ev_index, pk_index), 'Warning', f'Low CFT: {cft_max}')
                print(f' - Warning! Low CFT: {cft.max()}')
                continue

            spectro = []
            find = False
            for c in compo:
                trace = st.select(component=c)[0]
                s_rate = trace.stats.sampling_rate
                nb_pts = int(WINDOW_LENGTH * s_rate)

                fft_list = []
                time_used = []
                start = trace.stats.starttime
                END = trace.stats.endtime

                while start + WINDOW_LENGTH <= END:
                    tr = trace.slice(starttime=start,
                                     endtime=start + WINDOW_LENGTH)

                    mean_time = tr.stats.starttime + (WINDOW_LENGTH / 2)
                    time_used.append(mean_time - trace.stats.starttime)
                    start += (WINDOW_LENGTH * OVERLAP)

                    fft, _ = get_fft(tr, WINDOW_LENGTH, OVERLAP, nb_pts)

                    fft = np.array(fft)
                    fft_list.append(fft)

                fft_list = np.array(fft_list)
                if fft_list.shape == (237, 50):  # OVERLAP 75% : (237,50)
                    fft_list /= fft_list.max()
                    spectro.append(fft_list)
                    find = True
                else:
                    err = f'fft_list.shape != (237,50) ({fft_list.shape})'
                    append_cell((ev_index, pk_index), 'Error', err)
                    print(f' - Error! {err}')

            if find is True and len(spectro) == 3:
                spectro = np.array(spectro)
                os.makedirs(f'{spectro_dir}/{ev_index}', exist_ok=True)
                stream_name = (p_path.split('/')[-1]).split('.mseed')[0]
                np.save(f'{spectro_dir}/{ev_index}/{stream_name}.npy', spectro)
                append_cell((ev_index, pk_index), 'Compo', compo)
            else:
                err = f'find is {find} and len(spectro) == {len(spectro)}'
                append_cell((ev_index, pk_index), 'Error', err)
    return eventos
