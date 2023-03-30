from dataclasses import dataclass
from pprint import pprint
from typing import Iterator, List
from audiostream2py import PyAudioSourceReader, AudioSegment
from creek.infinite_sequence import (
    BufferedGetter,
    OverlapsPastError,
)
from datetime import datetime, timedelta


@dataclass
class InfiniteAudioSequence:
    iterator: Iterator[AudioSegment]
    buffer_len: int

    def __post_init__(self):
        self.buffer_getter = BufferedGetter(self.buffer_len)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.slice(item)
        else:
            raise TypeError(f'{type(self).__name__}.__getitem__: Unhandled {item=}')

    def slice(self, s: slice):
        if len(self) == 0 or self.tail.end_date < s.stop:
            self.fill_to_stop_date(s.stop)

        if self.head.start_date > s.start:
            raise OverlapsPastError(
                f'You asked for {s}, but the buffer only contains the index range: '
                f'{self.head.start_date}:{self.tail.end_date}'
            )

        def query(chunk: AudioSegment):
            return chunk.end_date > s.start and chunk.start_date <= s.stop

        chunks = self.buffer_getter[query]
        return self.trim_and_merge_audio_data(chunks, s.start, s.stop)

    @staticmethod
    def trim_and_merge_audio_data(chunks: List[AudioSegment], start, stop):
        chunks[0] = chunks[0][start:]
        chunks[-1] = chunks[-1][:stop]
        return AudioSegment.concatenate(chunks)

    def fill_to_stop_date(self, stop):
        for ad in self.iterator:
            self.buffer_getter.append(ad)
            if stop is None or ad.end_date > stop:
                break

    def __len__(self):
        return len(self.buffer_getter._deque)

    @property
    def head(self) -> AudioSegment:
        return self.buffer_getter._deque[0]

    @property
    def tail(self) -> AudioSegment:
        return self.buffer_getter._deque[-1]


if __name__ == '__main__':
    pprint(PyAudioSourceReader.list_recording_devices())

    INPUT_DEVICE = None
    CHUNK = 44100
    WIDTH = 2
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5
    QUERY_SECONDS = 3.5
    BUFFER_LEN = PyAudioSourceReader.audio_buffer_size_seconds_to_maxlen(
        buffer_size_seconds=RECORD_SECONDS, rate=RATE, frames_per_buffer=CHUNK
    )

    source_reader = PyAudioSourceReader(
        rate=RATE,
        width=WIDTH,
        channels=CHANNELS,
        frames_per_buffer=CHUNK,
        input_device_index=INPUT_DEVICE,
    )

    with source_reader.stream_buffer(maxlen=1) as stream_buffer:

        buffer_reader = stream_buffer.mk_reader()

        audio = InfiniteAudioSequence(buffer_reader, buffer_len=BUFFER_LEN)
        now_plus_1 = datetime.now() + timedelta(seconds=1)
        bt = int(now_plus_1.timestamp() * 1000000)
        tt = int((now_plus_1 + timedelta(seconds=QUERY_SECONDS)).timestamp() * 1000000)
        audio_data = audio[bt:tt]
        print(audio_data)
        print('Waveform seconds:', len(audio_data.waveform) / WIDTH / CHANNELS / RATE)
