"""
An app that loads either a wav file from local folder or records a sound
and visualizes the resulting numpy array 
"""
from functools import partial
from typing import List, Mapping
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
from streamlitfront.elements import (
    FileUploader,
)

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
)

from olab.base import mk_step, mk_pipeline, learn_outlier_model, apply_fitted_model


def mk_pipeline_maker_app_with_mall(
    mall: Mapping,
    *,
    step_factories: str = "step_factories",
    steps: str = "steps",
    steps_store=None,
    pipelines: str = "pipelines",
    pipelines_store=None,
    data: str = "data",
    data_store=None,
    learned_models=None,
    models_scores=None,
):

    if not b.mall():
        b.mall = mall
    mall = b.mall()
    if not b.selected_step_factory():
        b.selected_step_factory = "chunker"  # TODO make this dynamic

    crudifier = partial(Crudifier, mall=mall)

    steps_store = steps_store or steps
    data_store = data_store or data
    pipelines_store = pipelines_store or pipelines

    mk_step_crudified = crudifier(
        param_to_mall_map=dict(step_factory=step_factories), output_store=steps_store
    )(mk_step)

    #
    mk_pipeline_crudified = crudifier(
        output_store=pipelines_store,
    )(mk_pipeline)

    learn_outlier_model_crudified = crudifier(
        param_to_mall_map=dict(
            tagged_data="sound_output", preprocess_pipeline="pipelines"
        ),
        output_store="learned_models",
    )(learn_outlier_model)

    apply_fitted_model_crudified = crudifier(
        param_to_mall_map=dict(
            tagged_data="sound_output",
            preprocess_pipeline="pipelines",
            fitted_model="learned_models",
        ),
        output_store="models_scores",
    )(apply_fitted_model)

    @crudifier(
        param_to_mall_map=dict(pipeline=pipelines_store),
    )
    def visualize_pipeline(pipeline: LineParametrized):

        return pipeline

    @crudifier(
        param_to_mall_map=dict(scores="models_scores"),
    )
    def visualize_scores(scores, threshold=80, num_segs=3):

        intervals = scores_to_intervals(scores, threshold, num_segs)

        return scores, intervals

    @crudifier(output_store="sound_output")
    def upload_sound(train_audio: List[WaveForm], tag: str):
        return train_audio, tag

    def get_step_name(step):
        return [k for k, v in mall[steps].items() if v == step][0]

    def get_selected_step_factory_sig():
        selected_step_factory = mall["step_factories"].get(
            b.selected_step_factory.get()
        )
        if selected_step_factory:
            return Sig(selected_step_factory)

    config = {
        APP_KEY: {"title": "Data Preparation"},
        RENDERING_KEY: {
            "upload_sound": {
                # NAME_KEY: "Data Loader",
                "execution": {
                    "inputs": {
                        "train_audio": {
                            ELEMENT_KEY: FileUploader,
                            "type": "wav",
                            "accept_multiple_files": True,
                        },
                    },
                    "output": {
                        ELEMENT_KEY: SuccessNotification,
                        "message": "Wav files loaded successfully.",
                    },
                },
            },
            "display_tag_sound": {
                "execution": {
                    "output": {
                        ELEMENT_KEY: AudioArrayDisplay,
                    },
                },
            },
            "mk_step_crudified": {
                NAME_KEY: "Pipeline Step Maker",
                "execution": {
                    "inputs": {
                        "step_factory": {
                            "value": b.selected_step_factory,
                        },
                        "kwargs": {"func_sig": get_selected_step_factory_sig},
                    },
                    "output": {
                        ELEMENT_KEY: SuccessNotification,
                        "message": "The step has been created successfully.",
                    },
                },
            },
            "mk_pipeline_crudified": {
                NAME_KEY: "Pipeline Maker",
                "execution": {
                    "inputs": {
                        steps: {
                            ELEMENT_KEY: PipelineMaker,
                            "items": list(mall[steps].values()),
                            "serializer": get_step_name,
                        },
                    },
                    "output": {
                        ELEMENT_KEY: SuccessNotification,
                        "message": "The pipeline has been created successfully.",
                    },
                },
            },
            "exec_pipeline": {
                NAME_KEY: "Pipeline Executor",
                "execution": {
                    "inputs": {
                        "pipeline": {
                            "value": b.selected_pipeline,
                        },
                        "data": {
                            ELEMENT_KEY: SelectBox,
                            "options": mall["sound_output"],
                        },
                    }
                },
            },
            "visualize_pipeline": {
                NAME_KEY: "Pipeline Visualization",
                "execution": {
                    "inputs": {
                        "pipeline": {
                            "value": b.selected_pipeline,
                        },
                    },
                    "output": {
                        ELEMENT_KEY: GraphOutput,
                        NAME_KEY: "Flow",
                        "use_container_width": True,
                    },
                },
            },
            "visualize_scores": {
                NAME_KEY: "Scores Visualization",
                "execution": {
                    "output": {
                        ELEMENT_KEY: ArrayWithIntervalsPlotter,
                    },
                },
            },
            "simple_model": {
                NAME_KEY: "Learn model",
                "execution": {
                    "output": {
                        ELEMENT_KEY: ArrayPlotter,
                    },
                },
            },
            "apply_fitted_model": {
                NAME_KEY: "Apply model",
                "execution": {
                    "output": {
                        ELEMENT_KEY: ArrayPlotter,
                    },
                },
            },
        },
    }

    funcs = [
        upload_sound,
        mk_step_crudified,
        mk_pipeline_crudified,
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


if __name__ == "__main__":

    app = mk_pipeline_maker_app_with_mall(
        mall, step_factories="step_factories", steps="steps", pipelines="pipelines"
    )

    app()
