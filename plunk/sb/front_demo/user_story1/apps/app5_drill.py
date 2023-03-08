"""
An app that loads either a wav file from local folder or records a sound
and visualizes the resulting numpy array 
"""
from functools import partial
from typing import List, Mapping, Iterable, Callable
from i2 import FuncFactory, Sig
from lined import LineParametrized

from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from front.crude import Crudifier
from streamlitfront import mk_app, binder as b
from streamlitfront.elements import (
    SelectBox,
    SuccessNotification,
    PipelineMaker,
)
from streamlitfront.elements import FileUploader

from olab.types import (
    Step,
    Pipeline,
    WaveForm,
    AudioArrayDisplay,
    GraphOutput,
    ArrayPlotter,
)
from olab.util import (
    simple_chunker,
    scores_to_intervals,
    simple_featurizer,
    ArrayWithIntervalsPlotter,
    clean_dict,
)

from olab.base import learn_outlier_model, apply_fitted_model


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
        result = Step(step=step, step_factory=step_factory)
        return result

    @crudifier(
        param_to_mall_map=dict(step_to_modify=steps_store), output_store=steps_store
    )
    def modify_step(step_to_modify: Step, kwargs: dict):

        kwargs = clean_dict(kwargs)  # TODO improve that logic
        step_factory = step_to_modify.step_factory
        step = partial(step_factory, **kwargs)()
        return Step(step=step, step_factory=step_factory)

    @crudifier(output_store=pipelines_store,)
    def mk_pipeline(steps: Iterable[Callable]):
        named_funcs = [(get_step_name(step), step) for step in steps]
        pipeline = Pipeline(steps=steps, pipe=LineParametrized(*named_funcs))
        return pipeline

    @crudifier(
        param_to_mall_map=dict(pipeline=pipelines_store), output_store=pipelines_store,
    )
    def modify_pipeline(pipeline, steps):
        named_funcs = [(get_step_name(step), step) for step in steps]
        pipe = LineParametrized(*named_funcs)
        return Pipeline(steps=named_funcs, pipe=pipe)

    learn_outlier_model_crudified = crudifier(
        param_to_mall_map=dict(
            tagged_data='sound_output', preprocess_pipeline='pipelines'
        ),
        output_store='learned_models',
    )(learn_outlier_model)

    apply_fitted_model_crudified = crudifier(
        param_to_mall_map=dict(
            tagged_data='sound_output',
            preprocess_pipeline='pipelines',
            fitted_model='learned_models',
        ),
        output_store='models_scores',
    )(apply_fitted_model)

    @crudifier(param_to_mall_map=dict(pipeline=pipelines_store),)
    def visualize_pipeline(pipeline: Pipeline):

        return pipeline

    @crudifier(param_to_mall_map=dict(scores='models_scores'),)
    def visualize_scores(scores, threshold=80, num_segs=3):

        intervals = scores_to_intervals(scores, threshold, num_segs)

        return scores, intervals

    @crudifier(output_store='sound_output')
    def upload_sound(train_audio: List[WaveForm], tag: str):
        return train_audio, tag

    def get_step_name(step):
        return [k for k, v in mall[steps].items() if v.step == step][0]

    def get_selected_step_factory_sig():
        selected_step_factory = mall['step_factories'].get(
            b.selected_step_factory.get()
        )
        if selected_step_factory:
            return Sig(selected_step_factory)

    def get_step_to_modify_factory_sig():
        selected_step_factory = (
            mall['steps'].get(b.selected_step_to_modify.get()).step_factory
        )
        if selected_step_factory:
            return Sig(selected_step_factory)

    def on_select_pipeline(pipeline):
        b.steps_of_selected_pipeline.set(mall['pipelines'][pipeline].steps)

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
            'modify_step': {
                NAME_KEY: 'Modify Step',
                'execution': {
                    'inputs': {
                        'step_to_modify': {'value': b.selected_step_to_modify,},
                        'kwargs': {'func_sig': get_step_to_modify_factory_sig},
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
                            'items': [v.step for v in mall[steps].values()],
                            'serializer': get_step_name,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The pipeline has been created successfully.',
                    },
                },
            },
            'modify_pipeline': {
                NAME_KEY: 'Pipeline Modify',
                'execution': {
                    'inputs': {
                        'pipeline': {
                            ELEMENT_KEY: SelectBox,
                            'value': b.selected_pipeline,
                            'on_value_change': on_select_pipeline,
                        },
                        steps: {
                            ELEMENT_KEY: PipelineMaker,
                            'items': [v.step for v in mall[steps].values()],
                            'steps': b.steps_of_selected_pipeline(),
                            'serializer': get_step_name,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The pipeline has been modified successfully.',
                    },
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
        mk_step,
        modify_step,
        mk_pipeline,
        modify_pipeline,
        learn_outlier_model_crudified,
        apply_fitted_model_crudified,
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


if __name__ == '__main__':

    app = mk_pipeline_maker_app_with_mall(
        mall, step_factories='step_factories', steps='steps', pipelines='pipelines'
    )

    app()
