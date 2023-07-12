import numpy as np
from creek.automatas import BasicAutomata, mapping_to_transition_func
from typing import Callable, MutableMapping, Any, Mapping, Literal
from dataclasses import dataclass
from i2 import ch_names
from pprint import pprint
import numpy as np
from creek import BufferStats
from statistics import mean
from collections import deque
from audiostream2py import AudioSegment
from recode import decode_pcm_bytes
from scipy import special
from sklearn.preprocessing import StandardScaler

Case = Any
Cases = Mapping[Case, Callable]


RecordingCommands = Literal["start", "resume", "stop"]


def get_bytes_of_audio_segment(audio_segment: AudioSegment) -> bytes:
    return audio_segment.waveform


def convert_bytes_to_array(bytes_: bytes, dtype: type) -> np.ndarray:
    return np.frombuffer(bytes_, dtype=dtype)


def convert_array_to_bool(array: np.ndarray) -> np.ndarray:
    return array != 0


def audio_segment_to_int(audio_segment: AudioSegment) -> np.ndarray:
    bytes_ = get_bytes_of_audio_segment(audio_segment)
    array = convert_bytes_to_array(bytes_, dtype=np.int16)
    bool_array = convert_array_to_bool(array)
    int_array = bool_array.astype(np.int8)
    return list(int_array)


def plc_segment_to_bool(plc_segment: AudioSegment) -> np.ndarray:
    return np.array(decode_pcm_bytes(plc_segment.waveform))


def get_audio_ts_from_index(audio_segment: AudioSegment, index: int) -> tuple:
    return audio_segment.get_ts_of_frame_index(index)


def get_bt_of_ts(ts: tuple):
    return ts[0]


edges_ones_idx = (lambda edges: [i for i, x in enumerate(edges) if x == 1],)
ts_for_edge_one = (
    lambda edges_ones_idx, plc_segment: [
        get_audio_ts_from_index(plc_segment, i) for i in edges_ones_idx
    ],
)


@dataclass
class RecordingSwitchBoard:
    store: MutableMapping = None
    _current_key = None

    def start(self, key, chk):
        self._current_key = key
        self.store[key] = []
        self._append(chk)

    def resume(self, key, chk):
        print(f'resume called')
        self._append(chk)

    def stop(self, key, chk):
        self._append(chk)
        self._current_key = None

    def _append(self, chk):
        if self._current_key is None:
            raise ValueError("Cannot append without first starting recording.")
        self.store[self._current_key].extend(chk)

    @property
    def is_recording(self):
        return self._current_key is not None


@dataclass
class SimpleSwitchCase:
    """A functional implementation of thw switch-case control flow.
    Makes a callable that takes two arguments, a case and an input.

    >>> f = SimpleSwitchCase({'plus_one': lambda x: x + 1, 'times_two': lambda x: x * 2})
    >>> f('plus_one', 2)
    3
    >>> f('times_two', 2)
    4
    """

    cases: Mapping[Case, Callable]

    def __call__(self, case, input):
        func = self.cases.get(case, None)
        if func is None:
            raise ValueError(f"Case {case} not found.")
        return func(input)


def mk_simple_switch_case(
    cases: Cases, *, name: str = None, case_name: str = None, input_name: str = None
):
    """
    Makes a simple switch-case function, with optional naming control.
    """
    switch_case_func = SimpleSwitchCase(cases)
    switch_case_func = ch_names(
        switch_case_func, **dict(case=case_name, input=input_name)
    )
    if name is not None:
        switch_case_func.__name__ = name
    return switch_case_func


def mk_recorder_switch(
    store, *, mk_recorder: Callable[[MutableMapping], Any] = RecordingSwitchBoard
):
    recorder = mk_recorder(store)
    return mk_simple_switch_case(
        {
            "start": lambda key_and_chk: recorder.start(*key_and_chk),
            "resume": lambda key_and_chk: recorder.resume(*key_and_chk),
            "stop": lambda key_and_chk: recorder.stop(*key_and_chk),
            "waiting": lambda x: None,
        },
        name="recorder_switch",
        case_name="state",
        input_name="key_and_chk",
    )


def mk_transition_func(
    trans_func_mapping,
    initial_state,  # symbol_var_name: str,
):
    recording_state_transition_func = mapping_to_transition_func(
        trans_func_mapping,
        strict=False,
    )
    transitioner = BasicAutomata(
        transition_func=recording_state_transition_func,
        state=initial_state,
    )

    # @i2.ch_names(symbol=symbol_var_name)
    def transition(symbol):
        return transitioner.transition(symbol)

    # transition = transitioner.reset().transition

    return transition


class AudioSegmentProcessorOld:
    write_state = False
    buffered_segment = [AudioSegment.empty()]  # [] is better

    def __call__(self, segment, ts=None):
        if isinstance(ts, list):
            ts = ts[0]
        if (not self.write_state) and ts is None:
            return None
        if (not self.write_state) and ts:
            self.buffered_segment = [segment[ts:]]
            self.write_state = True
        if self.write_state and ts is None:
            self.buffered_segment += [segment]
        if self.write_state and ts:
            result = self.buffered_segment + [segment[:ts]]
            self.buffered_segment = [segment[ts:]]
            return result


def sum_none(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return a + b


class AudioSegmentProcessor_addition:
    write_state = False
    buffered_segment = None

    def __call__(self, segment, ts=None):
        if isinstance(ts, list):
            ts = ts[0]
        if (not self.write_state) and ts is None:
            return None
        elif (not self.write_state) and ts:
            self.buffered_segment = segment[ts:]
            self.write_state = True
        elif self.write_state and ts is None:
            self.buffered_segment = sum_none(self.buffered_segment, segment)
        elif self.write_state and ts:
            result = sum_none(self.buffered_segment, segment[:ts])
            self.buffered_segment = segment[ts:]
            return result


class AudioSegmentProcessor:
    write_state = False
    buffered_segment = AudioSegment.empty()  # use something more general

    def __call__(self, segment, ts=None):
        if isinstance(ts, list):
            ts = ts[0]
        if (not self.write_state) and ts is None:
            return None
        elif (not self.write_state) and ts:
            self.buffered_segment = segment[ts:]
            self.write_state = True
            return None
        elif self.write_state and ts is None:
            self.buffered_segment = AudioSegment.concatenate(
                [self.buffered_segment, segment]
            )
            return None
        elif self.write_state and ts:
            result = AudioSegment.concatenate([self.buffered_segment, segment[:ts]])
            self.buffered_segment = segment[ts:]
            return result


def mk_audio_segment_processor():
    return AudioSegmentProcessor()


def rising(d):
    x, y = d
    return int(x < y)


def mk_event_detector(values=(0,), maxlen=2, func=rising):
    bs = BufferStats(values=values, maxlen=maxlen, func=func)

    def detector(segment):
        return [bs(item) for item in segment]

    return detector


def append_if_not_none(l, item):
    if not item is None:
        l.append(item)

    return l


def mk_buffer(values=(0.0,), maxlen=5, func=mean, add_new_val=deque.append):
    bs = BufferStats(values=values, maxlen=maxlen, func=func, add_new_val=add_new_val)
    return bs


def flatten(l):
    res = []
    for item in l:
        if isinstance(item, list):
            res.extend(item)
        else:
            res.append(item)
    return res


def plot_rising_edges(wf_segment, ts_list):
    import matplotlib.pyplot as plt

    frames = [wf_segment._nearest_frame_index(ts) for ts in ts_list if ts]

    x_max = max(frames)
    _, ax = plt.subplots(1, 1, figsize=(20, 10))
    ax.plot(convert_bytes_to_array(wf_segment.waveform, dtype=np.int16)[:x_max])
    for frame in frames:
        ax.axvline(x=frame, color='r')
    plt.show()


# simple model


def cdf(x, mu, sigma):
    return 1.0 / 2 + 1.0 / 2 * special.erf((np.log(x) - mu) / (np.sqrt(2) * sigma))


def log_normal_pdf(x, mu, sigma):
    return np.exp(-((np.log(x) - mu) ** 2) / (2 * sigma**2)) / (
        x * sigma * np.sqrt(2 * np.pi)
    )


def check_arr(X):
    from sklearn.utils.validation import check_array

    try:
        check_array(X, ensure_2d=True)
    except ValueError:
        return X.reshape(-1, 1)


class LogNormal:
    def __init__(self) -> None:
        self.scaler = StandardScaler()

    def fit(self, X):
        self.partial_fit(X)
        return self

    def partial_fit(self, X):
        X = check_arr(X)
        self.scaler.partial_fit(np.log(X))
        self.mu = self.scaler.mean_
        self.sigma = self.scaler.scale_

        return self

    def predict(self, X):
        return cdf(X, self.mu, self.sigma)


def mk_model():
    return LogNormal()


# trans_func_mapping = {
#     ("waiting", 1): "start",
#     ("start", 0): "resume",
#     ("start", 1): "stop",
#     ("resume", 1): "stop",
#     ("stop", 0): "waiting",
#     ("stop", 1): "start",
# }

# trans_func_mapping = {
#     ("w", 1): "n",
#     ("n", 0): "c",
#     #("n", 1): "c",
#     ("c", 1): "n",
#     #("c", 0): "w",
#     #("stop", 0): "start",
#     #("stop", 1): "start",
# }
trans_func_mapping = {
    (0, 1): 1,
    (1, 1): 0,
    (1, 0): 0,
    (0, 0): 0,
    # ("c", 0): "w",
    # ("stop", 0): "start",
    # ("stop", 1): "start",
}
plc_symbols = ['00', '01', '10', '11']  # ['a', 'b', 'c', 'd']


def extract_edge_indices_from_bool_segment(
    bool_segment: np.ndarray, last_sample_of_previous_segment: bool, edge_type: str
) -> list:
    int_segment = bool_segment.astype(int)
    prepend = int(last_sample_of_previous_segment)
    edges = np.diff(int_segment, prepend=prepend)
    if edge_type == 'rising':
        edge_value = 1
    elif edge_type == 'descending':
        edge_value = -1
    return (edges == edge_value).nonzero()[0].tolist()
