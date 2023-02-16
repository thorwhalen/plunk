from itertools import count

import pytest
from audiostream2py import AudioData, PaStatusFlags, PyAudioSourceReader

from plunk.ap.stream2py_creek.infinite_sequence import AudioDataGetter


def audio_data_gen(rate: int, width: int, channels: int, frames_per_buffer: int):
    def timestamp(x):
        return x * 1e6 * frames_per_buffer / rate

    def mock_pcm_bytes(fill_value: int):
        return fill_value.to_bytes(width, 'little') * channels * frames_per_buffer

    for i in count():
        yield AudioData(
            start_date=timestamp(i),
            end_date=timestamp(i + 1),
            waveform=mock_pcm_bytes(fill_value=i),
            frame_count=frames_per_buffer,
            status_flags=PaStatusFlags.paNoError,
        )


@pytest.mark.parametrize(
    'rate, width, channels, frames_per_buffer, bt, tt',
    [
        (1e6, 2, 1, 1000, 0 + 1, 5 * 1e6),
        (1e6, 2, 1, 1000, 2 * 1e6 + 1, 5 * 1e6),
        (1e2, 2, 1, 1000, 0 * 1e6 + 1, 5 * 1e6),
        (1e6, 2, 1, 1000, 2.000001 * 1e6 + 1.000001, 5 * 1e6),
    ],
)
def test_audio_data_getter(
    rate: int, width: int, channels: int, frames_per_buffer: int, bt, tt
):
    ad_it = audio_data_gen(rate, width, channels, frames_per_buffer)

    getter = AudioDataGetter(
        ad_it,
        buffer_len=PyAudioSourceReader.audio_buffer_size_seconds_to_maxlen(
            buffer_size_seconds=(tt - bt) * 2 / 1e6,
            rate=rate,
            frames_per_buffer=frames_per_buffer,
        ),
    )
    audio = getter[bt:tt]
    # timestamps are within one sample of requested time
    assert bt - 1e6 / rate <= audio.start_date
    assert audio.start_date <= bt + 1e6 / rate

    assert tt - 1e6 / rate <= audio.end_date
    assert audio.end_date <= tt + 1e6 / rate
