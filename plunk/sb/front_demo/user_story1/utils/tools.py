import numpy as np

from functools import partial
from typing import Iterable

from plunk.sb.front_experiments.streamlitfront_dataprep.data_prep2 import (
    # DFLT_WF_PATH,
    # DFLT_ANNOT_PATH,
    data_from_wav_folder,
)
import soundfile as sf
from io import BytesIO
import matplotlib.pyplot as plt

###### ML Tools ###########################
from omodel.gen_utils.chunker import fixed_step_chunker
from omodel.outliers.pystroll import OutlierModel as Stroll

DFLT_CHK_SIZE = 2048
DFLT_CHK_STEP = 2048

# Chunkers
def simple_chunker(it, chk_size: int = DFLT_CHK_SIZE):
    return fixed_step_chunker(it=it, chk_size=chk_size, chk_step=chk_size)


DFLT_CHUNKER = simple_chunker
# Featurizers
DFLT_FEATURIZER = lambda chk: np.abs(np.fft.rfft(chk))

featurizer = DFLT_FEATURIZER
chunker = simple_chunker
WaveForm = Iterable[int]


def store_to_key_fvs(wf_store, chunker=DFLT_CHUNKER, featurizer=DFLT_FEATURIZER):
    wf_items = wf_store.items()
    key_chk_tuples = fanout_and_flatten(wf_items, chunker, 1)
    featurizer_iter = partial(apply_func_to_index, apply_to_idx=1, func=featurizer)
    yield from map(featurizer_iter, key_chk_tuples)


def key_fvs_to_tag_fvs(key_fvs, annots_df):
    func = partial(key_to_tag_from_annots, annots_df=annots_df)
    tagger = partial(apply_func_to_index, apply_to_idx=0, func=func)

    yield from map(tagger, key_fvs)


def key_to_tag_from_annots(key, annots_df):
    tag = annots_df["tag"][annots_df["key"] == key].values[0]
    return tag


def mk_Xy(tag_fv_iterator):
    y, X = zip(*list(tag_fv_iterator))
    return np.array(X), y


DFLT_CHAIN = (({"type": "pca", "args": {"n_components": 5}},),)


def preprocess(X_train, n_components=5):

    from shaded.chained_spectral_projector import learn_chain_proj_matrix

    chain = DFLT_CHAIN
    chain["args"]["n_components"] = n_components
    proj_matrix = learn_chain_proj_matrix(X_train, chain=chain)
    X_train_proj = np.dot(X_train, proj_matrix)

    return proj_matrix, X_train_proj


def simple_model(tagged_data):
    sound, tag = tagged_data
    if not isinstance(sound, str):
        sound = sound.getvalue()

    arr = sf.read(BytesIO(sound), dtype="int16")[0]

    wfs = np.array(arr)
    st.write(f"wfs = {wfs[:200]}")
    chks = list(chunker(wfs, chk_size=DFLT_CHK_SIZE))
    fvs = np.array(list(map(featurizer, chks)))
    model = Stroll(n_centroids=50)
    model.fit(X=fvs)
    scores = model.score_samples(X=fvs)
    return scores
