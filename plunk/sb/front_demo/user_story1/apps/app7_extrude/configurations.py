# import streamlitfront.tools as t
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from streamlitfront.elements import (
    FileUploader,
    SuccessNotification,
    PipelineMaker,
)
from streamlitfront import binder as b
from i2 import Sig

# from streamlitfront.tools import trans_output


# render_image_url = t.Pipe(t.html_img_wrap, t.render_html,)
# render_bullet = t.Pipe(t.lines_to_html_paragraphs, t.text_to_html, t.render_html,)


# trans_output(config, 'topic_points', render_bullet)
# trans_output(config, 'get_illustration', render_image_url)
# trans_output(config, 'aggregate_story_and_image', t.dynamic_trans)


def mk_config(api):
    def on_select_step_factory(step_factory_name):
        step_factory = b.step_factories().get(step_factory_name)
        sig = Sig(step_factory) if step_factory else Sig()
        b.selected_step_factory_sig.set(sig)

    # def on_select_step_to_modify(step_name):
    #     step_factory_sig = api.get_step_factory_sig(step_name)
    #     b.selected_step_to_modify_sig.set(step_factory_sig)

    # def on_select_pipeline_to_modify(pipeline_name):
    #     pipeline = api.get_pipeline(pipeline_name)
    #     b.steps_of_selected_pipeline.set(pipeline.steps)

    _init_cache('sessions', api.list_sessions())
    _init_cache('step_factories', mall['step_factories'])
    _init_cache('step_names', api.get_store_keys('steps'))

    return {
        APP_KEY: {'title': 'Otosense Platform PoC'},
        RENDERING_KEY: {
            'upload_audio_data': {
                # NAME_KEY: "Data Loader",
                'execution': {
                    'inputs': {
                        'audio_data': {
                            ELEMENT_KEY: FileUploader,
                            'type': 'wav',
                            'accept_multiple_files': True,
                        }
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'Wav files loaded successfully.',
                    },
                    'on_submit': lambda output: _invalidate_cache('sessions'),
                },
            },
            'mk_step': {
                NAME_KEY: 'Pipeline Step Maker',
                'execution': {
                    'inputs': {
                        'step_factory': {
                            'value': b.selected_step_factory,
                            'on_value_change': on_select_step_factory,
                        },
                        'kwargs': {'func_sig': b.selected_step_factory_sig},
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The step has been created successfully.',
                    },
                    'on_submit': lambda output: _invalidate_cache('step_names'),
                },
            },
            # "modify_step": {
            #     NAME_KEY: "Modify Step",
            #     "execution": {
            #         "inputs": {
            #             "step_to_modify": {
            #                 "value": b.selected_step_to_modify,
            #                 "on_value_change": on_select_step_to_modify,
            #             },
            #             "kwargs": {"func_sig": b.selected_step_to_modify_sig},
            #         },
            #         "output": {
            #             ELEMENT_KEY: SuccessNotification,
            #             "message": "The step has been modified successfully.",
            #         },
            #         "on_submit": lambda output: _invalidate_cache('step_names'),
            #     },
            # },
            'mk_pipeline': {
                NAME_KEY: 'Pipeline Maker',
                'execution': {
                    'inputs': {
                        'steps': {ELEMENT_KEY: PipelineMaker, 'items': b.step_names(),},
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The pipeline has been created successfully.',
                    },
                },
            },
            # "modify_pipeline": {
            #     NAME_KEY: "Modify Pipeline",
            #     "execution": {
            #         "inputs": {
            #             "pipeline": {
            #                 "value": b.selected_pipeline,
            #                 "on_value_change": on_select_pipeline_to_modify,
            #             },
            #             "steps": {
            #                 ELEMENT_KEY: PipelineMaker,
            #                 "items": b.step_names(),
            #                 "steps": b.steps_of_selected_pipeline(),
            #             },
            #         },
            #         "output": {
            #             ELEMENT_KEY: SuccessNotification,
            #             "message": "The step has been modified successfully.",
            #         },
            #     },
            # },
            'learn_outlier_model': {
                NAME_KEY: 'Train Model',
                'execution': {
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The model has been trained successfully.',
                    },
                },
            },
            'apply_fitted_model': {
                NAME_KEY: 'Test Model',
                'execution': {'output': {ELEMENT_KEY: ArrayPlotter,},},
            },
            'visualize_output': {
                'execution': {'output': {ELEMENT_KEY: ArrayWithIntervalsPlotter,},},
            },
            Callable: {
                'execution': {'inputs': {'save_name': {NAME_KEY: 'Save as',},},},
            },
            'visualize_session': {
                'execution': {
                    'inputs': {
                        'session': {
                            ELEMENT_KEY: OtoTable,
                            'sessions': b.sessions,
                            'is_multiselect': False,
                        },
                    },
                    'output': {ELEMENT_KEY: WfVisualizePlayer},
                    'auto_submit': True,
                },
            },
        },
    }


def _init_cache(key, init_value):
    if not b[key]():
        b[key].set(init_value)


def _invalidate_cache(key):
    b[key].set(None)
