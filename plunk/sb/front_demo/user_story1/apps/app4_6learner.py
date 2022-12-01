"""
An app that loads either a wav file from local folder or records a sound
and visualizes the resulting numpy array 
"""
from typing import Mapping
from know.boxes import *
from functools import partial
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from front.crude import Crudifier
from lined import LineParametrized
import numpy as np

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import (
    SelectBox,
    SuccessNotification,
)
from streamlitfront.elements import FileUploader

import soundfile as sf
from io import BytesIO
from plunk.sb.front_demo.user_story1.components.components import ArrayPlotter
from plunk.sb.front_demo.user_story1.utils.tools import (
    DFLT_FEATURIZER,
    DFLT_CHK_SIZE,
    chunker,
    WaveForm,
    Stroll,
)
from typing import List
import streamlit as st


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


DFLT_PIPELINE = LineParametrized(simple_chunker, simple_featurizer)


def mk_pipeline_maker_app_with_mall(
    mall: Mapping,
    *,
    pipelines: str = None,
    sound_output: str = None,
    models_scores: str = None
):
    if not b.mall():
        b.mall = mall
    mall = b.mall()
    # if not b.selected_step_factory():
    #     b.selected_step_factory = 'chunker'  # TODO make this dynamic

    crudifier = partial(Crudifier, mall=mall)

    @crudifier(
        param_to_mall_map=dict(tagged_data='sound_output', pipeline='pipelines',),
        output_store='models_scores',
    )
    def learn_apply_model(tagged_data, pipeline):
        n_centroids = 15
        sound, _ = tagged_sounds_to_single_array(*tagged_data)
        wfs = np.array(sound)
        wfs = assert_dims(wfs)

        fvs = pipeline(wfs)
        model = Stroll(n_centroids=n_centroids)
        fitted_model = model.fit(X=fvs)
        scores = fitted_model.score_samples(X=fvs)
        return scores

    @crudifier(output_store='sound_output')
    def upload_sound(train_audio: List[WaveForm], tag: str):

        return train_audio, tag

    config = {
        APP_KEY: {'title': 'Data Preparation'},
        RENDERING_KEY: {
            'upload_sound': {
                # NAME_KEY: "Data Loader",
                'execution': {
                    'inputs': {
                        'train_audio': {
                            ELEMENT_KEY: FileUploader,
                            'type': 'wav',
                            'accept_multiple_files': True,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'Wav files loaded successfully.',
                    },
                },
            },
            'learn_apply_model': {
                NAME_KEY: 'Apply model',
                'execution': {
                    # "inputs": {
                    #     "tagged_data": {
                    #         ELEMENT_KEY: SelectBox,
                    #         "options": mall["sound_output"], #must be a list, when explicit
                    #     },
                    #     # "pipeline": {
                    #     #     ELEMENT_KEY: SelectBox,
                    #     #     "options": mall["pipelines"],
                    #     # },
                    #     # "pipeline": {
                    #     #     "value": b.selected_pipeline,
                    #     # },
                    # },
                    'output': {ELEMENT_KEY: ArrayPlotter,},
                },
            },
        },
    }

    funcs = [
        upload_sound,
        learn_apply_model,
    ]
    app = mk_app(funcs, config=config)

    return app


if __name__ == '__main__':

    mall = dict(sound_output=dict(), pipelines=dict(), models_scores=dict(),)

    # crudifier = partial(prepare_for_crude_dispatch, mall=mall)
    mall['sound_output'] = dict()
    mall['pipelines'] = dict(
        # ML
        default_pipeline=DFLT_PIPELINE
    )
    # st.write(mall)

    app = mk_pipeline_maker_app_with_mall(
        mall, pipelines='pipelines', sound_output='sound_output'
    )

    app()
