from streamlitfront.examples import simple_ml_1 as sml
from know.boxes import *
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY
from streamlitfront import mk_app, binder as b
from typing import Mapping
from dol import Pipe
from operator import methodcaller
from pathlib import Path
import numpy as np
from recode import decode_wav_bytes
from plunk.sb.front_demo.user_story1.components.components import ArrayPlotter
from i2 import Sig, rm_params
from i2.util import PicklableLambda

from front.dag import crudify_funcs
from meshed import code_to_dag


from meshed.dag import ch_funcs, ch_func_node_func
from i2.signatures import _fill_defaults_and_annotations


def compare_signatures_by_inserting_defaults(func1, func2):
    sig1 = Sig(func1)
    sig2 = Sig(func2)
    sig_1_from_2 = _fill_defaults_and_annotations(sig1, sig2)
    sig_2_from_1 = _fill_defaults_and_annotations(sig2, sig1)

    return sig_1_from_2 == sig_2_from_1


ch_func_node_func2 = partial(
    ch_func_node_func, compare_func=compare_signatures_by_inserting_defaults
)

# Create a dag
@code_to_dag
def audio_anomalies():
    wf = get_audio(audio_source)
    # model = train(wf, learner)
    model = train(wf)

    results = apply(model, wf)
    view = display_results(results)


# filepath = /Users/sylvain/Dropbox/Otosense/VacuumEdgeImpulse/train/noise.AirConditioner_2.9.1440000-1600000.wav.23q8e34o.ingestion-6bc8b65f8c-vrv59.wav

file_to_bytes = Pipe(Path, methodcaller("read_bytes"))
wav_file_to_array = Pipe(
    file_to_bytes,
    decode_wav_bytes,
    itemgetter(0),
    np.array,
    np.transpose,
    itemgetter(0),
)


def get_sound(audio_source):
    return wav_file_to_array(audio_source)


def visualize_results(results):
    return results


def view_array(arr_str):
    return np.array(arr_str)


func_mapping = dict(
    get_audio=get_sound,
    train=rm_params(
        sml.auto_spectral_anomaly_learner,
        allow_removal_of_non_defaulted_params=True,
        params_to_remove=[
            "learner",
            "chk_size",
            "chk_step",
            "n_features",
            "n_centroids",
            "log_factor",
        ],
    ),
    apply=PicklableLambda(lambda model, wf: model(wf), name="step3"),
    display_results=visualize_results,
)
audio_anomalies = ch_funcs(
    audio_anomalies, func_mapping=func_mapping, ch_func_node_func=ch_func_node_func2
)

print(f'{Sig(func_mapping["train"])=}')
# filepath = '/Users/thorwhalen/Dropbox/_odata/sound/engines/aircraft/Aircraft Engine 01.wav'
filepath = "/Users/sylvain/Dropbox/_odata/sound/guns/01 Gunshot Pistol - Small Caliber - 18 Versions.wav"


def mk_pipeline_maker_app_with_mall(
    mall: Mapping,
    *,
    pipelines: str = None,
    sound_output: str = None,
    models_scores: str = None,
):

    if not b.mall():
        b.mall = mall
    mall = b.mall()

    _funcs = crudify_funcs(var_nodes="wf model results", dag=audio_anomalies, mall=mall)

    def debug_check_mall():
        st.write(mall)
        return None

    def result_viewer(key):
        results = mall["results_store"][key]
        return results

    step1, step2, step3, step4 = _funcs  # remove list

    # step3 = partial(step3, save_name="a_result")
    # step3.__name__ = "step3"
    # print(f"{Sig(step3)=}")

    config = {
        APP_KEY: {"title": "Data Preparation"},
        RENDERING_KEY: {
            "visualize_results": {
                # NAME_KEY: "Apply model",
                "execution": {
                    "output": {
                        ELEMENT_KEY: ArrayPlotter,
                    },
                },
            },
        },
    }

    funcs = [
        step1,
        step2,
        step3,
        step4,
        # result_viewer,
        debug_check_mall,
    ]

    app = mk_app(funcs, config=config)

    return app


if __name__ == "__main__":
    import streamlit as st

    mall = dict()

    app = mk_pipeline_maker_app_with_mall(mall)

    app()
