"""
An app that loads either a wav file from local folder or records a sound
and visualizes the resulting numpy array 
"""
from dataclasses import dataclass
from functools import partial
from typing import Callable, Iterable, List, Mapping
from i2 import FuncFactory, Sig
from lined import LineParametrized
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from io import BytesIO
from more_itertools import consecutive_groups

from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from front.crude import Crudifier
from front.elements import OutputBase
from streamlitfront import mk_app, binder as b
from streamlitfront.elements import (
    SelectBox,
    SuccessNotification,
    PipelineMaker,
)
from streamlitfront.elements import FileUploader
import streamlit as st

from omodel.gen_utils.chunker import fixed_step_chunker
from omodel.outliers.pystroll import OutlierModel as Stroll


DFLT_CHK_SIZE = 2048
DFLT_FEATURIZER = lambda chk: np.abs(np.fft.rfft(chk))
DFLT_NUM_OUTLIERS = 3
WaveForm = Iterable[int]


def simple_chunker(wfs, chk_size: int = DFLT_CHK_SIZE):
    return list(fixed_step_chunker(wfs, chk_size=chk_size))


def apply_func_to_index_groups(func, arr, idx_groups):
    """
    Applies func to the slices of array arr specified by the groups
    """
    result = [func(arr[gp]) for gp in idx_groups]

    return result


def arg_top_max(arr, num_elements):
    """
    returns the largest num_elements from the array arr
    """
    result = [arr.index(i) for i in sorted(arr, reverse=True)][:num_elements]
    return result


def clean_dict(kwargs):
    result = {k: v for k, v in kwargs.items() if v != ''}
    return result


def indices_for_percentile(arr, low=0, high=100):
    return np.percentile(arr, [low, high])


def consecutive_indices(arr):
    return list(map(list, consecutive_groups(arr)))


def get_groups_extremities_all(
    arr, groups_indices, func=np.mean, num_outliers=DFLT_NUM_OUTLIERS,
):

    means = apply_func_to_index_groups(func, arr, groups_indices)
    arg = arg_top_max(means, num_outliers)
    result = [
        (groups_indices[idx][0], groups_indices[idx][-1])
        for idx, _ in enumerate(means)
        if idx in arg
    ]

    return result


def scores_to_intervals(scores, high_percentile=90, num_selected=3):
    [low, high] = list(indices_for_percentile(scores, low=0, high=high_percentile))
    arr_selected = np.nonzero(scores >= high)[0]
    groups_indices = consecutive_indices(arr_selected)
    intervals_all = get_groups_extremities_all(
        scores, groups_indices, func=np.mean, num_outliers=num_selected,
    )
    result = [(a, b) for a, b in intervals_all if b > a]

    return result


def simple_featurizer(chks):
    fvs = np.array(list(map(DFLT_FEATURIZER, chks)))
    return fvs


def tagged_sound_to_array(train_audio: WaveForm, tag: str):
    sound, tag = train_audio, tag
    if not isinstance(sound, bytes):
        sound = sound.getvalue()

    arr = sf.read(BytesIO(sound), dtype='int16')[0]
    return arr, tag


def tagged_sounds_to_single_array(train_audio: List[WaveForm], tag: str):
    sounds, tag = train_audio, tag
    result = []
    for sound in sounds:
        # if not isinstance(sound, bytes):
        sound = sound.getvalue()
        arr = sf.read(BytesIO(sound), dtype='int16')[0]
        result.append(arr)
    # print(np.hstack(result))
    return np.hstack(result).reshape(-1, 1), tag


def assert_dims(wfs):
    if wfs.ndim >= 2:
        wfs = wfs[:, 0]
    return wfs


@dataclass
class AudioArrayDisplay(OutputBase):
    def render(self):
        sound, tag = self.output
        # if not isinstance(sound, str):
        if not isinstance(sound, bytes):

            sound = sound.getvalue()

        arr = sf.read(BytesIO(sound), dtype='int16')[0]
        # st.write(type(arr))
        tab1, tab2 = st.tabs(['Audio Player', 'Waveform'])
        with tab1:
            # if not isinstance(sound, bytes):
            #     sound = sound.getvalue()
            # arr = sf.read(BytesIO(sound), dtype="int16")[0]
            st.write(f'type of data={type(sound)}')

            st.audio(sound)
        with tab2:
            fig, ax = plt.subplots(figsize=(15, 5))
            ax.plot(arr, label=f'Tag={tag}')
            ax.legend()
            st.pyplot(fig)
            # st.write(arr[:10])


@dataclass
class GraphOutput(OutputBase):
    use_container_width: bool = False

    def render(self):
        # with st.expander(self.name, True): #cannot nest expanders
        dag = self.output
        st.graphviz_chart(
            figure_or_dot=dag.dot_digraph(),
            use_container_width=self.use_container_width,
        )


@dataclass
class ArrayPlotter(OutputBase):
    def render(self):
        X = self.output
        # st.write(f"Average score of session= {np.mean(X)}")
        fig, ax = plt.subplots(figsize=(15, 5))
        ax.plot(X)
        ax.legend()
        st.pyplot(fig)


@dataclass
class ArrayWithIntervalsPlotter(OutputBase):
    def render(self):
        X, intervals = self.output
        fig = pyplot_with_intervals(X, intervals)
        st.pyplot(fig)


def pyplot_with_intervals(X, intervals=None):
    min_x = np.mean(X)
    xs = list(range(len(X)))
    ys = X
    fig, ax = plt.subplots(figsize=(7, 2))
    ax.plot(xs, ys, linewidth=1)
    if intervals:
        for i, interval in enumerate(intervals):
            start, end = interval
            plt.axvspan(start, end, facecolor='g', alpha=0.5)

            ax.annotate(f'{i}', xy=(start, min_x), ha='left', va='top')
    return fig


def mk_pipeline_maker_app_with_mall(
    mall: Mapping,
    *,
    step_factories: str = 'step_factories',
    steps: str = 'steps',
    steps_store=None,
    pipelines: str = 'pipelines',
    pipelines_store=None,
    data: str = 'data',
    data_store=None,
    learned_models=None,
    models_scores=None,
):
    if not b.mall():
        b.mall = mall
    mall = b.mall()
    if not b.selected_step_factory():
        b.selected_step_factory = 'chunker'  # TODO make this dynamic

    crudifier = partial(Crudifier, mall=mall)

    steps_store = steps_store or steps
    data_store = data_store or data
    pipelines_store = pipelines_store or pipelines

    @crudifier(
        param_to_mall_map=dict(step_factory=step_factories), output_store=steps_store
    )
    def mk_step(step_factory: Callable, kwargs: dict):
        kwargs = clean_dict(kwargs)  # TODO improve that logic
        step = partial(step_factory, **kwargs)()

        return step

    #
    @crudifier(output_store=pipelines_store,)
    def mk_pipeline(steps: Iterable[Callable]):
        return LineParametrized(*steps)

    @crudifier(
        param_to_mall_map=dict(pipeline=pipelines_store, tagged_data='sound_output'),
        output_store='exec_outputs',
    )
    def exec_pipeline(pipeline: Callable, tagged_data):

        sound, _ = tagged_sound_to_array(*tagged_data)
        wfs = np.array(sound)
        wfs = assert_dims(wfs)

        result = pipeline(wfs)
        return result

    @crudifier(
        param_to_mall_map=dict(
            tagged_data='sound_output', preprocess_pipeline='pipelines'
        ),
        output_store='learned_models',
    )
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
    def apply_fitted_model(tagged_data, preprocess_pipeline, fitted_model):
        sound, tag = tagged_sounds_to_single_array(*tagged_data)
        wfs = np.array(sound)
        wfs = assert_dims(wfs)

        fvs = preprocess_pipeline(wfs)
        scores = fitted_model.score_samples(X=fvs)
        return scores

    @crudifier(param_to_mall_map=dict(pipeline=pipelines_store),)
    def visualize_pipeline(pipeline: LineParametrized):

        return pipeline

    @crudifier(param_to_mall_map=dict(scores='models_scores'),)
    def visualize_scores(scores, threshold=80, num_segs=3):

        intervals = scores_to_intervals(scores, threshold, num_segs)

        return scores, intervals

    @crudifier(output_store='sound_output')
    def upload_sound(train_audio: List[WaveForm], tag: str):
        # sound, tag = train_audio, tag
        # if not isinstance(sound, bytes):
        #     sound = sound.getvalue()

        # arr = sf.read(BytesIO(sound), dtype='int16')[0]
        # return arr, tag
        return train_audio, tag

    @crudifier(param_to_mall_map={'result': 'sound_output'})
    def display_tag_sound(result):
        return result

    def get_step_name(step):
        return [k for k, v in mall[steps].items() if v == step][0]

    def get_selected_step_factory_sig():
        selected_step_factory = mall['step_factories'].get(
            b.selected_step_factory.get()
        )
        if selected_step_factory:
            return Sig(selected_step_factory)

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
            'display_tag_sound': {
                'execution': {'output': {ELEMENT_KEY: AudioArrayDisplay,},},
            },
            'mk_step': {
                NAME_KEY: 'Pipeline Step Maker',
                'execution': {
                    'inputs': {
                        'step_factory': {'value': b.selected_step_factory,},
                        'kwargs': {'func_sig': get_selected_step_factory_sig},
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The step has been created successfully.',
                    },
                },
            },
            'mk_pipeline': {
                NAME_KEY: 'Pipeline Maker',
                'execution': {
                    'inputs': {
                        steps: {
                            ELEMENT_KEY: PipelineMaker,
                            'items': list(mall[steps].values()),
                            'serializer': get_step_name,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The pipeline has been created successfully.',
                    },
                },
            },
            'exec_pipeline': {
                NAME_KEY: 'Pipeline Executor',
                'execution': {
                    'inputs': {
                        'pipeline': {'value': b.selected_pipeline,},
                        'data': {
                            ELEMENT_KEY: SelectBox,
                            'options': mall['sound_output'],
                        },
                    }
                },
            },
            'visualize_pipeline': {
                NAME_KEY: 'Pipeline Visualization',
                'execution': {
                    'inputs': {'pipeline': {'value': b.selected_pipeline,},},
                    'output': {
                        ELEMENT_KEY: GraphOutput,
                        NAME_KEY: 'Flow',
                        'use_container_width': True,
                    },
                },
            },
            'visualize_scores': {
                NAME_KEY: 'Scores Visualization',
                'execution': {'output': {ELEMENT_KEY: ArrayWithIntervalsPlotter,},},
            },
            'simple_model': {
                NAME_KEY: 'Learn model',
                'execution': {'output': {ELEMENT_KEY: ArrayPlotter,},},
            },
            'apply_fitted_model': {
                NAME_KEY: 'Apply model',
                'execution': {'output': {ELEMENT_KEY: ArrayPlotter,},},
            },
        },
    }

    funcs = [
        upload_sound,
        # display_tag_sound,
        mk_step,
        mk_pipeline,
        learn_outlier_model,
        apply_fitted_model,
        # exec_pipeline,
        visualize_pipeline,
        visualize_scores,
    ]
    app = mk_app(funcs, config=config)

    return app


mall = dict(
    # Factory Input Stores
    sound_output=dict(),
    step_factories=dict(
        # ML
        chunker=FuncFactory(simple_chunker),
        featurizer=FuncFactory(simple_featurizer),
    ),
    # Output Store
    data=dict(),
    steps=dict(),
    pipelines=dict(),
    exec_outputs=dict(),
    learned_models=dict(),
    models_scores=dict(),
)

# crudifier = partial(prepare_for_crude_dispatch, mall=mall)

# step_factories = dict(
#     # ML
#     chunker=FuncFactory(simple_chunker),
#     featurizer=FuncFactory(simple_featurizer),
# )

# mall['step_factories'] = step_factories


if __name__ == '__main__':

    app = mk_pipeline_maker_app_with_mall(
        mall, step_factories='step_factories', steps='steps', pipelines='pipelines'
    )

    app()
