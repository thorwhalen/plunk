from typing import Callable

import numpy as np
from hum import (
    mk_sine_wf,
    DFLT_N_SAMPLES,
    DFLT_SR,
    wf_with_timed_bleeps,
    freq_based_stationary_wf,
    pure_tone,
)

from plunk.ap.wf_visualize_player.wf_visualize_player_element import (
    WfVisualizePlayer,
    WfSr,
)

DFLT_N_SAMPLES = 10 * DFLT_N_SAMPLES  # 10 sec


def wf_sine() -> WfSr:
    return (
        mk_sine_wf(freq=10, n_samples=DFLT_N_SAMPLES, sr=DFLT_SR, phase=0.25, gain=1),
        DFLT_SR,
    )


def wf_bleeps() -> WfSr:
    return (
        wf_with_timed_bleeps(
            n_samples=DFLT_N_SAMPLES, bleep_loc=16 * 4, bleep_spec=16, sr=DFLT_SR,
        )
        / 2 ** 15,
        DFLT_SR,
    )


def wf_mix() -> WfSr:
    return (
        freq_based_stationary_wf(
            freqs=(2, 5, 37, 100), weights=None, n_samples=DFLT_N_SAMPLES, sr=DFLT_SR,
        ),
        DFLT_SR,
    )


def wf_pure_tone() -> WfSr:
    return (
        pure_tone(chk_size=DFLT_N_SAMPLES, freq=1000, sr=DFLT_SR, max_amplitude=2 ** 15)
        / 2 ** 15,
        DFLT_SR,
    )


def wf_two_channel_sine_tone() -> WfSr:
    s, _ = wf_sine()
    t, sr = wf_pure_tone()
    return np.array([s, t]), sr


def wf_three_channel_mixed_sine_tone() -> WfSr:
    m, _ = wf_mix()
    s, _ = wf_sine()

    t, sr = wf_pure_tone()
    return np.array([m, s, t]), sr


if __name__ == '__main__':
    from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
    from streamlitfront import mk_app

    sounds = [
        wf_sine,
        wf_bleeps,
        wf_mix,
        wf_pure_tone,
        wf_two_channel_sine_tone,
        wf_three_channel_mixed_sine_tone,
    ]

    def mk_rendering(wf_func: Callable):
        key = wf_func.__name__
        name = ' '.join(key.split('_')[1:])
        # description = f'{name} waveform'
        return (
            key,
            {
                NAME_KEY: name,
                # 'description': {'content': description},
                'execution': {
                    'output': {ELEMENT_KEY: WfVisualizePlayer},
                    'auto_submit': True,
                },
            },
        )

    app = mk_app(
        sounds,
        config={
            APP_KEY: {'title': 'Waveform Visualization Player'},
            RENDERING_KEY: {k: v for k, v in map(mk_rendering, sounds)},
        },
    )
    app()
