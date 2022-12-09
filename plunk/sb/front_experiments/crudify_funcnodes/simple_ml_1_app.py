from streamlitfront.examples import simple_ml_1 as sml
from know.boxes import *
from streamlitfront.elements import FileUploader
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from streamlitfront import mk_app, binder as b
from typing import Mapping


from front.dag import crudify_funcs


# filepath = /Users/sylvain/Dropbox/Otosense/VacuumEdgeImpulse/train/noise.AirConditioner_2.9.1440000-1600000.wav.23q8e34o.ingestion-6bc8b65f8c-vrv59.wav


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
    store = dict()
    mall['wf_store'] = store
    audio_anomalies = sml.audio_anomalies

    it = crudify_funcs(var_nodes='wf model results', dag=audio_anomalies, mall=mall)
    # it = crudify_funcs(var_nodes="wf", dag=audio_anomalies, mall=mall)
    print(audio_anomalies.synopsis_string())

    step1, step2, step3 = list(it)

    config = {
        APP_KEY: {'title': 'Data Preparation'},
        RENDERING_KEY: {
            'step1': {
                'execution': {
                    'inputs': {
                        'audio_source': {
                            ELEMENT_KEY: FileUploader,
                            'type': 'wav',
                            'accept_multiple_files': True,
                        },
                    },
                },
            },
            # "learn_apply_model": {
            #     NAME_KEY: "Apply model",
            #     #'execution': {'output': {ELEMENT_KEY: ArrayPlotter,},},
            # },
        },
    }
    funcs = [step1]
    app = mk_app(funcs, config=config)

    return app


if __name__ == '__main__':

    mall = dict(
        # sound_output=dict(),
        # pipelines=dict(),
        # models_scores=dict(),
    )

    app = mk_pipeline_maker_app_with_mall(mall)

    app()
