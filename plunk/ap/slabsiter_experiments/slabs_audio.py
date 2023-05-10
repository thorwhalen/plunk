import time
from functools import partial
from pprint import pprint

from audiostream2py.file import WavFileSourceReader
from audiostream2py.data import AudioSegment
from meshed.slabs import Slabs

from plunk.ap.snippets import PLUNK_ROOT_PATH

plc_file = PLUNK_ROOT_PATH / 'sb/slabsiter_experiments/data/PLC.wav'
accel_file = PLUNK_ROOT_PATH / 'sb/slabsiter_experiments/data/1621346260226336_ch2.wav'
assert plc_file.is_file(), f'File not found: {plc_file}'
assert accel_file.is_file(), f'File not found: {accel_file}'


def find_wf_at_event(wf_buffer, plc_event: AudioSegment):
    if plc_event is None:
        return
    event_start = plc_event.start_date
    event_end = plc_event.end_date
    return wf_buffer[event_start:event_end]


def plc_with_event(plc: AudioSegment):
    if b'\xff' in plc.waveform:
        return plc


plc_source = WavFileSourceReader(plc_file, frames_per_buffer=50, start_date=0)
accel_source = WavFileSourceReader(accel_file, frames_per_buffer=12800, start_date=0)

print('plc info:')
pprint(plc_source.info)
print('accel info:')
pprint(accel_source.info)

with accel_source.stream_buffer(maxlen=None) as accel_buffer:
    accel_reader = accel_buffer.mk_reader()
    with plc_source.stream_buffer(maxlen=None) as plc_buffer:
        plc_reader = plc_buffer.mk_reader()

        time.sleep(1)
        next_plc = partial(plc_reader.next, ignore_no_item_found=True)

        slabs = Slabs(
            wf_buffer=lambda: accel_reader,
            plc=next_plc,
            plc_event=plc_with_event,
            wf_at_event=find_wf_at_event,
        )

        for s in slabs:
            print(f'{s=}')

            if wf := s.get('wf_at_event'):
                print(wf.waveform[:44])
                break
