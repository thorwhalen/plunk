from streamlitfront.examples import simple_ml_1 as sml
from know.boxes import *

# from streamlitfront.elements import FileUploader
# from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
# from streamlitfront import mk_app, binder as b
# from typing import Mapping
# from dol import Pipe
# from operator import methodcaller
from pathlib import Path

# import numpy as np
# from recode import decode_wav_bytes
# from plunk.sb.front_demo.user_story1.components.components import ArrayPlotter
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


# file_to_bytes = Pipe(Path, methodcaller("read_bytes"))
# wav_file_to_array = Pipe(
#     file_to_bytes,
#     decode_wav_bytes,
#     itemgetter(0),
#     np.array,
#     np.transpose,
#     itemgetter(0),
# )

from i2 import include_exclude, rm_params, Pipe
from recode import decode_wav_bytes


def get_sound(audio_source):
    return decode_wav_bytes(Path(audio_source).read_bytes())[0]


from operator import methodcaller
import numpy as np


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


# def get_sound(audio_source):
#     import soundfile as sf

#     return sf.read(audio_source)[0]


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
    # apply=lambda model, wf: model(wf),
    apply=apply_func,
)
audio_anomalies = ch_funcs(
    audio_anomalies, func_mapping=func_mapping, ch_func_node_func=ch_func_node_func2
)

if __name__ == "__main__":
    import platform

    computer_name = platform.node()

    if computer_name == "TWHALEN-M03":
        # source = '/Users/thorwhalen/Dropbox/_odata/oto/proj/Guns/Pistol/Unsupressed/Single Shot/Glock 17 9mm/Glock 17 9mm_Xxsv00000_1.wav'
        source = "/Users/thorwhalen/Dropbox/_odata/oto/proj/OD/data/sample_wavs/1563212051653.wav"

    else:  # sylvain's
        source = "/Users/sylvain/Dropbox/_odata/sound/guns/01 Gunshot Pistol - Small Caliber - 18 Versions.wav"

    print(Sig(func_mapping["train"]))
    mall = dict()
    audio_anomalies(source)
    result = crudify_func_nodes(
        var_nodes="wf model results", dag=audio_anomalies, mall=mall
    )

    result(source)
