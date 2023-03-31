from typing import List, Union

import os
import soundfile as sf
import numpy as np

from olab.base import simple_chunker, simple_featurizer
from olab.types import WaveForm
from omodel.outliers.pystroll import OutlierModel as Stroll
from meshed import code_to_dag

Path = Union[str, os.PathLike]

# simple uploader of wav files
def read_sound(sound: Path):
    arr, _ = sf.read(sound, dtype='int16')
    return arr


def upload_sound(wav_list: List[Path]) -> List[WaveForm]:
    arrs = [read_sound(wav) for wav in wav_list]
    return np.hstack(arrs)


# ML steps
def learn_model(fvs, n_centroids=5):
    model = Stroll(n_centroids=n_centroids)
    model.fit(X=fvs)

    return model


def apply_model(fvs, fitted_model):
    scores = fitted_model.score_samples(X=fvs)
    return scores


d = {
    'upload_sound': upload_sound,
    'simple_chunker': simple_chunker,
    'simple_featurizer': simple_featurizer,
    'learn_model': learn_model,
    'apply_model': apply_model,
}

# simple DPP in form of a DAG
@code_to_dag(func_src=d)
def simple_dpp(wfs: List[WaveForm]):
    wfs = upload_sound(wav_list)
    chks = simple_chunker(wfs)
    fvs = simple_featurizer(chks)
    model = learn_model(fvs)
    scores = apply_model(fvs, model)


if __name__ == '__main__':
    # make input data for test
    from pyckup import grab
    from io import BytesIO

    f1 = grab('https://www.dropbox.com/s/yueb7mn6mo6abxh/0_0.wav?dl=0')
    f2 = grab('https://www.dropbox.com/s/hruf3u7oufx6fqg/0_1.wav?dl=0')

    wav_list = [BytesIO(f1), BytesIO(f2)]

    # run the experiment
    scores = simple_dpp(wav_list)

    print(scores)
