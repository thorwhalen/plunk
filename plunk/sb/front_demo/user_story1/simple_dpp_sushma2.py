import numpy as np

from olab.base import simple_chunker, simple_featurizer
from olab.types import WaveForm
from omodel.outliers.pystroll import OutlierModel as Stroll
from meshed import code_to_dag
from recode import decode_wav_bytes
from py2json import Ctor


def bytes_to_wf(wav_bytes: bytes) -> WaveForm:
    wf, sr = decode_wav_bytes(wav_bytes)
    return np.array(wf)


# ML steps
def learn_model(fvs, n_centroids=5):
    model = Stroll(n_centroids=n_centroids)
    model.fit(X=fvs)

    return model


def apply_model(fvs, fitted_model):
    scores = fitted_model.score_samples(X=fvs)
    return scores


d = {
    "bytes_to_wf": bytes_to_wf,
    "simple_chunker": simple_chunker,
    "simple_featurizer": simple_featurizer,
    "learn_model": learn_model,
    "apply_model": apply_model,
    # "deconstruct": Ctor.deconstruct,
    # "construct": Ctor.construct,
}

# simple DPP in form of a DAG
@code_to_dag(func_src=d)
def simple_dpp(wav_bytes: bytes):
    wfs = bytes_to_wf(wav_bytes)
    chks = simple_chunker(wfs)
    fvs = simple_featurizer(chks)
    model = learn_model(fvs)
    # model_dict = model.to_jdict()
    # model_dict = deconstruct(model)
    # model_2 = construct(model_dict)
    # scores = apply_model(fvs, model_2)


if __name__ == "__main__":
    # make input data for testing purposes
    from pyckup import grab
    from pprint import pprint

    # from py2json impo

    # make a wf as a bytes object
    wf = grab("https://www.dropbox.com/s/yueb7mn6mo6abxh/0_0.wav?dl=0")

    # check the type
    print(f"{type(wf)=}")

    # # run the experiment
    model = simple_dpp(wf)
    model_dict = model.to_jdict()
    # result = model.to_jdict()
    pprint(model_dict)
