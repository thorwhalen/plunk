from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from plunk.ap.app4_drill_but_make_it_slabsiter.components import (
    get_selected_step_factory_sig,
    mall,
    get_step_name,
    upload_sound,
    mk_step,
    mk_pipeline,
    learn_outlier_model,
    apply_fitted_model,
    visualize_pipeline,
    visualize_scores,
    live_apply_fitted_model,
)

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import (
    SelectBox,
    SuccessNotification,
    PipelineMaker,
)
from streamlitfront.elements import FileUploader

from plunk.ap.live_graph.live_graph_data_buffer import GRAPH_TYPES
from plunk.ap.live_graph.live_graph_streamlitfront import DataGraph
from plunk.sb.front_demo.user_story1.components.components import (
    AudioArrayDisplay,
    GraphOutput,
    ArrayPlotter,
    ArrayWithIntervalsPlotter,
)

config = {
    APP_KEY: {'title': 'Data Preparation'},
    RENDERING_KEY: {
        'upload_sound': {
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
                    'steps': {
                        ELEMENT_KEY: PipelineMaker,
                        'items': list(mall['steps'].values()),
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
                    'data': {ELEMENT_KEY: SelectBox, 'options': mall['sound_output'],},
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
        'live_apply_fitted_model': {
            NAME_KEY: 'Apply model with Live Data',
            'description': {'content': 'Configure soundcard for data stream'},
            'execution': {
                'inputs': {
                    'input_device': {
                        ELEMENT_KEY: SelectBox,
                        'options': b.input_devices(),
                    },
                    'graph_types': {
                        ELEMENT_KEY: SelectBox,
                        'options': list(GRAPH_TYPES),
                    },
                },
                'output': {ELEMENT_KEY: DataGraph},
            },
        },
    },
}

funcs = [
    upload_sound,
    mk_step,
    mk_pipeline,
    learn_outlier_model,
    apply_fitted_model,
    visualize_pipeline,
    visualize_scores,
    live_apply_fitted_model,
]
app = mk_app(funcs, config=config)
app()
