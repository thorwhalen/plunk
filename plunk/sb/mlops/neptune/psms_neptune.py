from collections import Counter
import neptune
from psms import dacc
from typing import Iterable
from slang import mk_chk_fft, tile_fft
from slang import fixed_step_chunker
from functools import partial
from operator import attrgetter
import numpy as np
from dol import wrap_kvs, filt_iter, Pipe
import itertools
from omodel import CentroidSmoothing
from sklearn.metrics import f1_score

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import os

# Create a Neptune run object
run = neptune.init_run(
    project="sppbonnot/PSMS",
    api_token="eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vbmV3LXVpLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9uZXctdWkubmVwdHVuZS5haSIsImFwaV9rZXkiOiJmNGE4MmRkNi03OTQwLTQyMTItYTRmOS1jYjAzZDEyZGMyZTYifQ==",
)  # your credentials

# Track metadata and hyperparameters by assigning them to the run
run["algorithm"] = "CentroidSmoothing"

PARAMS = {
    "chk_size": 1000,
}
run["parameters"] = PARAMS


mydacc = dacc.mk_dacc()


def first_slash_component(x):
    return x.split("/")[0]


def prefix_filtered_store(store, prefix):
    if isinstance(prefix, str):
        return filt_iter(store, filt=lambda x: x.startswith(prefix))
    else:
        assert isinstance(prefix, Iterable)
        set_of_prefixes = prefix
        return filt_iter(
            store, filt=lambda x: first_slash_component(x) in set_of_prefixes
        )


chk_size = 1000
chunker = partial(fixed_step_chunker, chk_size=chk_size)
# fft = mk_chk_fft(chk_size=chk_size)


def chk_to_fv(chk):
    # return np.ravel(np.array(list(map(fft, np.array(chk).T))).T)
    return np.ravel(np.array(list(map(tile_fft, np.array(chk).T))).T)


matrix_to_fvs = Pipe(
    attrgetter("values"),  # equivalent: lambda x: x.value
    chunker,
    partial(map, chk_to_fv),  # equivalent: lambda chks: map(chk_to_fv, chks)
)


def featurizer_store(store):
    return wrap_kvs(store, obj_of_data=matrix_to_fvs)


# from functools import lru_cache

# @lru_cache
def get_full_matrix(store):
    return np.vstack(list(store.values()))


healthy = featurizer_store(prefix_filtered_store(mydacc.data, "Healthy"))
key_to_tag = lambda x: x.split(os.path.sep)[0]

tags = Counter((key_to_tag(x) for x in mydacc.data))
not_healthy_tags = tags.keys() - {"Healthy"}
not_healthy = featurizer_store(prefix_filtered_store(mydacc.data, not_healthy_tags))

# from tested import train_test_split_keys
# train_test_split_keys()

X_healthy = np.array(list(itertools.chain.from_iterable(healthy.values())))
y_healthy = ["healthy"] * len(X_healthy)
X_not_healthy = np.array(list(itertools.chain.from_iterable(not_healthy.values())))
y_not_healthy = ["not_healthy"] * len(X_not_healthy)

X = np.vstack([X_healthy, X_not_healthy])
y = np.hstack([y_healthy, y_not_healthy])

model = Pipeline(
    steps=[
        ("scale", StandardScaler()),
        ("pca", PCA(n_components=50)),
        ("model", CentroidSmoothing()),
    ]
)
model.fit(X, y)
preds = model.predict(X)
yy = list(map(int, y == "healthy"))
yy_pred = list(map(int, model.predict(X) == "healthy"))

run["train/accuracy"] = f1_score(yy, yy_pred)
run["train/psms"].track_files(
    "/Users/sylvain/Dropbox/_odata/sound/induction_motor_data"
)

# Stop the connection and synchronize the data with the Neptune servers
run.stop()
