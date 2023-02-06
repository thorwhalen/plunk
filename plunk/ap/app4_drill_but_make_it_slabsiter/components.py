from pathlib import Path
from know.boxes import *
from functools import partial
from typing import Callable, Iterable
from i2 import Sig
from front.crude import Crudifier
from lined import LineParametrized
import numpy as np

from streamlitfront import binder as b

import soundfile as sf
from io import BytesIO

from plunk.ap.app4_drill_but_make_it_slabsiter.file_store import (
    add_to_upload_files_store,
    upload_files_store,
    UploadFilesStore,
    pipeline_step_store,
    resolve_item_getter_args,
)
from plunk.ap.app4_drill_but_make_it_slabsiter.si_model import (
    dill_files,
    si_apply_fitted_model,
)
from plunk.ap.live_graph.audio_store import WavFileStore
from plunk.ap.live_graph.live_graph_data_buffer import mk_live_graph_data_buffer
from plunk.ap.live_graph.live_graph_streamlitfront import stop_stream
from plunk.ap.persist.persist import Persist
from plunk.ap.snippets import get_mall
from plunk.sb.front_demo.user_story1.utils.tools import (
    DFLT_FEATURIZER,
    DFLT_CHK_SIZE,
    chunker,
    WaveForm,
    Stroll,
    clean_dict,
    scores_to_intervals,
)
from typing import List


def simple_chunker(wfs, chk_size: int = DFLT_CHK_SIZE):
    return list(chunker(wfs, chk_size=chk_size))


def simple_featurizer(chks):
    fvs = np.array(list(map(DFLT_FEATURIZER, chks)))
    return fvs


def tagged_sounds_to_single_array(train_audio: List[WaveForm], tag: str):
    sounds, tag = train_audio, tag
    result = []
    for sound in sounds:
        sound = sound.getvalue()
        arr = sf.read(BytesIO(sound), dtype='int16')[0]
        result.append(arr)
    return np.hstack(result).reshape(-1, 1), tag


def assert_dims(wfs):
    if wfs.ndim >= 2:
        wfs = wfs[:, 0]
    return wfs


default_mall = dict(
    # Factory Input Stores
    sound_output={k: v for k, v in upload_files_store.getter_items()},
    step_factories=dict(
        # ML
        chunker=FuncFactory(simple_chunker),
        featurizer=FuncFactory(simple_featurizer),
    ),
    # Output Store
    data=dict(),
    steps={k: v for k, v in pipeline_step_store.getter_items()},
    pipelines=dict(),
    exec_outputs=dict(),
    learned_models=dict(),
    models_scores=dict(),
    source=None,
)

mall = get_mall(defaults=default_mall)
crudifier = partial(Crudifier, mall=mall)


@add_to_upload_files_store
@crudifier(output_store='sound_output')
def upload_sound(train_audio: List[WaveForm], tag: str):
    return train_audio, tag


def get_step_name(step):
    return [k for k, v in get_mall()['steps'].items() if v == step][0]


def _save_name_getter(args, kwargs, function=None, return_value=None):
    return kwargs['save_name']


@Persist.function_call(key_getter=_save_name_getter, store=pipeline_step_store)
@crudifier(param_to_mall_map=dict(step_factory='step_factories'), output_store='steps')
def mk_step(step_factory: Callable, kwargs: dict):
    kwargs = clean_dict(kwargs)
    step = partial(step_factory, **kwargs)()

    return step


def get_selected_step_factory_sig():
    selected_step_factory = get_mall()['step_factories'].get(
        b.selected_step_factory.get()
    )
    if selected_step_factory:
        return Sig(selected_step_factory)


@crudifier(output_store='pipelines',)
@resolve_item_getter_args
def mk_pipeline(steps: Iterable[Callable]):
    return LineParametrized(*steps)


@crudifier(
    param_to_mall_map=dict(tagged_data='sound_output', preprocess_pipeline='pipelines'),
    output_store='learned_models',
)
@UploadFilesStore.resolve_item_getter_args
def learn_outlier_model(tagged_data, preprocess_pipeline, n_centroids=5):

    sound, tag = tagged_sounds_to_single_array(*tagged_data)
    wfs = np.array(sound)

    wfs = assert_dims(wfs)

    fvs = preprocess_pipeline(wfs)
    model = Stroll(n_centroids=n_centroids)
    model.fit(X=fvs)

    return model


@crudifier(
    param_to_mall_map=dict(
        tagged_data='sound_output',
        preprocess_pipeline='pipelines',
        fitted_model='learned_models',
    ),
    output_store='models_scores',
)
@UploadFilesStore.resolve_item_getter_args
def apply_fitted_model(tagged_data, preprocess_pipeline, fitted_model):
    try:
        dill_files['tagged_data'] = tagged_data
    except Exception as e:
        print('tagged_data', e)
    try:
        dill_files['preprocess_pipeline'] = preprocess_pipeline
    except Exception as e:
        print('preprocess_pipeline', e)
    try:
        dill_files['fitted_model'] = fitted_model
    except Exception as e:
        print('fitted_model', e)
    sound, tag = tagged_sounds_to_single_array(*tagged_data)
    wfs = np.array(sound)
    wfs = assert_dims(wfs)

    fvs = preprocess_pipeline(wfs)
    scores = fitted_model.score_samples(X=fvs)
    return scores


@crudifier(param_to_mall_map=dict(pipeline='pipelines'),)
def visualize_pipeline(pipeline: LineParametrized):

    return pipeline


@crudifier(param_to_mall_map=dict(scores='models_scores'),)
def visualize_scores(scores, threshold=80, num_segs=3):

    intervals = scores_to_intervals(scores, threshold, num_segs)

    return scores, intervals


@crudifier(
    param_to_mall_map=dict(
        preprocess_pipeline='pipelines', fitted_model='learned_models',
    ),
    output_store='source',
)
def live_apply_fitted_model(
    preprocess_pipeline,
    fitted_model,
    input_device=None,
    rate=44100,
    width=2,
    channels=1,
    frames_per_buffer=44100,
    seconds_to_keep_in_stream_buffer=60,
    graph_types='volume',
):
    stop_stream()
    audio_store_rootdir = Path.cwd() / 'audio_store'
    audio_store_rootdir.mkdir(parents=True, exist_ok=True)
    audio_store = WavFileStore(rootdir=str(audio_store_rootdir))

    source = mk_live_graph_data_buffer(
        input_device,
        rate,
        width,
        channels,
        frames_per_buffer,
        seconds_to_keep_in_stream_buffer,
        graph_types,
        audio_store=audio_store,
        **si_apply_fitted_model(preprocess_pipeline, fitted_model),
    )
    source.start()
    return source
