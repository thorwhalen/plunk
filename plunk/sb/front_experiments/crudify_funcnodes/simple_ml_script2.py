from streamlitfront.examples import simple_ml_1 as sml
from know.boxes import *
from streamlitfront.elements import FileUploader
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from streamlitfront import mk_app, binder as b
from typing import Mapping
from dol import Pipe
from operator import methodcaller
from pathlib import Path
import numpy as np
from recode import decode_wav_bytes
from plunk.sb.front_demo.user_story1.components.components import ArrayPlotter
from i2 import Sig
from front.dag import crudify_funcs, crudify_func_nodes, _crudified_func_nodes
from meshed import code_to_dag

from plunk.sb.front_demo.user_story1.utils.funcs import (
    learn_apply_model,
    upload_sound,
)
from streamlitfront.elements import SelectBox
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


@code_to_dag
def audio_anomalies():
    wf = get_audio(audio_source)
    # model = train(wf, learner)
    model = train(wf)

    results = apply(model, wf)


def apply_func(model, wf):
    return model(wf)


from i2 import include_exclude, rm_params


def get_sound(audio_source):
    return audio_source


class MyClass:
    def __init__(self) -> None:
        pass


def fake_auto_spectral_anomaly_learner(wf, learner=MyClass(), chk_size=2048):
    return wf


func_mapping = dict(
    get_audio=get_sound,
    train=rm_params(
        # sml.auto_spectral_anomaly_learner, include="wf learner", exclude=""
        FuncFactory(fake_auto_spectral_anomaly_learner),
        allow_removal_of_non_defaulted_params=True,
        params_to_remove=[
            "learner",
            "chk_size",
        ],
    ),
    # apply=lambda model, wf: model(wf),
    apply=apply_func,
)
audio_anomalies = ch_funcs(
    audio_anomalies, func_mapping=func_mapping, ch_func_node_func=ch_func_node_func2
)

if __name__ == "__main__":
    from i2 import Sig

    source = "/Users/sylvain/Dropbox/_odata/sound/guns/01 Gunshot Pistol - Small Caliber - 18 Versions.wav"
    print(Sig(func_mapping["train"]))
    mall = dict()
    # audio_anomalies(source)
    _funcs = crudify_funcs(var_nodes="wf model results", dag=audio_anomalies, mall=mall)
    # result = crudify_func_nodes(
    #     var_nodes="wf model results", dag=audio_anomalies, mall=mall
    # )

    # result(source)
    step1, step2, step3 = _funcs
    print(f"{Sig(step1)}=")
    print(f"{Sig(step2)}=")
    print(f"{Sig(step3)}=")

    # wf = step1(source)
    # model = step2(wf)
    # print(Sig(model))
    # result = model(wf)
