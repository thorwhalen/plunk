from functools import partial

from hum import (
    mk_sine_wf,
    DFLT_N_SAMPLES,
    DFLT_SR,
    wf_with_timed_bleeps,
    freq_based_stationary_wf,
    pure_tone,
)


def wf_sine():
    return (
        mk_sine_wf(freq=20, n_samples=DFLT_N_SAMPLES, sr=DFLT_SR, phase=0.25, gain=3),
        DFLT_SR,
    )


def wf_bleeps():
    return (
        wf_with_timed_bleeps(
            n_samples=DFLT_N_SAMPLES, bleep_loc=1024 * 4, bleep_spec=1024, sr=DFLT_SR,
        ),
        DFLT_SR,
    )


def wf_mix():
    return (
        freq_based_stationary_wf(
            freqs=(2, 4, 6, 8), weights=None, n_samples=DFLT_N_SAMPLES, sr=DFLT_SR,
        ),
        DFLT_SR,
    )


def wf_pure_tone():
    return (
        pure_tone(chk_size=DFLT_N_SAMPLES, freq=440, sr=DFLT_SR, max_amplitude=30000),
        DFLT_SR,
    )
