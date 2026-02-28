"""RNC preprocessing and inference utilities."""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np


WINDOW_LENGTH_S = 1.0
STEP_LENGTH_S = 0.25  # 75% overlap
EXPECTED_SHAPE = (237, 50)
_MODEL_CACHE: dict[str, object] = {}


class InferenceError(RuntimeError):
    """Raised when preprocessing or inference cannot be completed."""


@dataclass(frozen=True)
class PreprocessResult:
    spectrogram: np.ndarray | None
    cft_max: float | None
    warning: str | None


def stride_windows(x: np.ndarray, n: int, noverlap: int | None = None, axis: int = 0) -> np.ndarray:
    """Legacy helper used to create FFT windows."""
    if noverlap is None:
        noverlap = 0
    if noverlap >= n:
        raise ValueError("noverlap must be less than n")
    if n < 1:
        raise ValueError("n cannot be less than 1")
    x = np.asarray(x)
    if x.ndim != 1:
        raise ValueError("only 1-dimensional arrays can be used")
    if n == 1 and noverlap == 0:
        if axis == 0:
            return x[np.newaxis]
        return x[np.newaxis].transpose()
    if n > x.size:
        raise ValueError("n cannot be greater than the length of x")

    noverlap = int(noverlap)
    n = int(n)
    step = n - noverlap
    if axis == 0:
        shape = (n, (x.shape[-1] - noverlap) // step)
        strides = (x.strides[0], step * x.strides[0])
    else:
        shape = ((x.shape[-1] - noverlap) // step, n)
        strides = (step * x.strides[0], x.strides[0])
    return np.lib.stride_tricks.as_strided(x, shape=shape, strides=strides)


def _fft_taper(data: np.ndarray) -> np.ndarray:
    from obspy.signal.invsim import cosine_taper

    return data * cosine_taper(npts=data.size, p=0.2)


def get_fft(trace, window_length_s: float, step_length_s: float) -> tuple[np.ndarray, np.ndarray]:
    """Compute FFT features for one 1-second trace segment."""
    import matplotlib.mlab as mlab

    s_rate = float(trace.stats.sampling_rate)
    nb_pts = int(window_length_s * s_rate)
    nb_overlap = int((1.0 - step_length_s) * nb_pts)
    window = _fft_taper(np.ones(nb_pts, trace.data.dtype))
    result = stride_windows(trace.data, nb_pts, nb_overlap, axis=0)
    result = mlab.detrend(result, mlab.detrend_linear, axis=0)
    result = result * window.reshape((-1, 1))
    num_freqs = nb_pts // 2 + 1
    result = np.fft.fft(result, n=nb_pts, axis=0)[:num_freqs, :]
    freqs = np.fft.fftfreq(nb_pts, 1 / s_rate)[:num_freqs]
    freqs[-1] *= -1
    result = result[1:]
    freqs = freqs[1:]
    result = np.abs(result) / trace.data.size
    result = result.ravel()
    return result, freqs


def _read_component_trace(path: str, channel: str):
    import obspy as op

    st = op.read(path, dtype=float)
    if len(st) == 0:
        raise InferenceError(f"empty stream: {path}")
    st.merge(method=1, fill_value="interpolate")
    tr = st[0].copy()
    tr.stats.channel = channel
    return tr


def _decimate_to_target_hz(trace, target_hz: float):
    sr = float(trace.stats.sampling_rate)
    if abs(sr - target_hz) < 1e-6:
        return trace
    if sr < target_hz:
        raise InferenceError(f"sampling rate below target ({sr} Hz < {target_hz} Hz)")
    factor = sr / target_hz
    rounded = int(round(factor))
    if abs(factor - rounded) > 1e-6 or rounded <= 1:
        raise InferenceError(f"sampling rate not integer-factor decimable to {target_hz} Hz: {sr} Hz")
    trace.decimate(rounded)
    return trace


def _spectrogram_for_trace(trace) -> np.ndarray:
    fft_list: list[np.ndarray] = []
    start = trace.stats.starttime
    end = trace.stats.endtime
    while start + WINDOW_LENGTH_S <= end:
        tr = trace.slice(starttime=start, endtime=start + WINDOW_LENGTH_S)
        start += STEP_LENGTH_S
        fft, _ = get_fft(tr, window_length_s=WINDOW_LENGTH_S, step_length_s=STEP_LENGTH_S)
        fft_list.append(np.array(fft))
    out = np.array(fft_list)
    if tuple(out.shape) != EXPECTED_SHAPE:
        raise InferenceError(f"invalid spectrogram shape {tuple(out.shape)} expected {EXPECTED_SHAPE}")
    vmax = float(out.max()) if out.size else 0.0
    if vmax <= 0.0:
        raise InferenceError("spectrogram max is zero")
    out /= vmax
    return out


def preprocess_triplet(
    *,
    component_paths: dict[str, str],
    merged_path: str | None,
    required_channels: list[str],
    target_hz: float,
    cft_min: float,
) -> PreprocessResult:
    """
    Read a 3C station-time triplet and return normalized spectrogram.

    Returns warning when CFT is below threshold; in this case spectrogram is None.
    """
    import obspy as op
    from obspy.signal.trigger import classic_sta_lta

    traces = []
    if merged_path:
        if not os.path.exists(merged_path):
            raise InferenceError(f"merged mseed not found: {merged_path}")
        st = op.read(merged_path, dtype=float)
        if len(st) == 0:
            raise InferenceError(f"empty merged stream: {merged_path}")
        st.merge(method=1, fill_value="interpolate")
        for ch in required_channels:
            selected = st.select(channel=ch)
            if len(selected) == 0:
                raise InferenceError(f"missing channel {ch} in merged mseed: {merged_path}")
            tr = selected[0].copy()
            tr.stats.channel = ch
            tr = _decimate_to_target_hz(tr, target_hz=target_hz)
            traces.append(tr)
    else:
        for ch in required_channels:
            path = component_paths[ch]
            if not os.path.exists(path):
                raise InferenceError(f"missing component file: {path}")
            tr = _read_component_trace(path, ch)
            tr = _decimate_to_target_hz(tr, target_hz=target_hz)
            traces.append(tr)

    stream = op.Stream(traces=traces)
    stream.detrend("demean")
    stream.taper(0.05)
    stream = stream.filter("highpass", freq=2, corners=4, zerophase=True)

    cft_max = 0.0
    for tr in stream:
        s_rate = float(tr.stats.sampling_rate)
        nsta = max(1, int(1 * s_rate))
        nlta = max(nsta + 1, int(5 * s_rate))
        cft = classic_sta_lta(tr.data, nsta, nlta)
        if cft.size:
            cft_max = max(cft_max, float(cft.max()))

    if cft_max < cft_min:
        return PreprocessResult(
            spectrogram=None,
            cft_max=cft_max,
            warning=f"low_cft:{cft_max:.6f}",
        )

    specs = []
    for ch in required_channels:
        trace = stream.select(channel=ch)
        if len(trace) == 0:
            raise InferenceError(f"missing channel after preprocessing: {ch}")
        specs.append(_spectrogram_for_trace(trace[0]))
    spectrogram = np.array(specs)
    if tuple(spectrogram.shape) != (3, EXPECTED_SHAPE[0], EXPECTED_SHAPE[1]):
        raise InferenceError(f"invalid stacked spectrogram shape {tuple(spectrogram.shape)}")
    return PreprocessResult(
        spectrogram=spectrogram,
        cft_max=cft_max,
        warning=None,
    )


def _load_model(model_path: str):
    import tensorflow as tf

    key = os.path.abspath(model_path)
    model = _MODEL_CACHE.get(key)
    if model is None:
        model = tf.keras.models.load_model(model_path, compile=False)
        _MODEL_CACHE[key] = model
    return model


def predict_spectrogram(*, model_path: str, spectrogram: np.ndarray) -> tuple[float, float, int, str]:
    """Run model inference for one spectrogram and return class probabilities."""
    model = _load_model(model_path)
    x = np.moveaxis(np.array([spectrogram]), 1, 3)
    output = model.predict(x, verbose=0)
    prob_nat = float(output[0][0])
    prob_ant = float(output[0][1])
    pred = int(np.argmax(output, axis=1)[0])
    label = "Natural" if pred == 0 else "Anthropogenic"
    return prob_nat, prob_ant, pred, label
