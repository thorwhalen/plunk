from streamlitfront.examples import simple_ml_1 as sml
from know.boxes import *
from streamlitfront.elements import FileUploader
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from streamlitfront import mk_app, binder as b


from front.dag import crudify_funcs
from front.crude import DillFiles
import os
from collections import defaultdict

mall = dict()
# mall = DillFiles(os.path.expanduser('~/tmp'))
# mall = defaultdict()

audio_anomalies = sml.audio_anomalies

it = crudify_funcs(var_nodes="wf model results", dag=audio_anomalies, mall=mall)
step1, step2, step3 = list(it)

from i2 import Sig

print(Sig(step1))

config = {
    APP_KEY: {"title": "Data Preparation"},
    RENDERING_KEY: {
        "step1": {
            "execution": {
                "inputs": {
                    "audio_source": {
                        ELEMENT_KEY: FileUploader,
                        "type": "wav",
                        "accept_multiple_files": True,
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
app()

# filepath = /Users/sylvain/Dropbox/Otosense/VacuumEdgeImpulse/train/noise.AirConditioner_2.9.1440000-1600000.wav.23q8e34o.ingestion-6bc8b65f8c-vrv59.wav
