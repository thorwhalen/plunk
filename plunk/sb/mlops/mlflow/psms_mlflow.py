from collections import Counter
from psms import dacc
from typing import Iterable
from slang import tile_fft
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

import warnings

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn

import logging

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


def first_slash_component(x):
    return x.split('/')[0]


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
    attrgetter('values'),  # equivalent: lambda x: x.value
    chunker,
    partial(map, chk_to_fv),  # equivalent: lambda chks: map(chk_to_fv, chks)
)


def featurizer_store(store):
    return wrap_kvs(store, obj_of_data=matrix_to_fvs)


# from functools import lru_cache

# @lru_cache
def get_full_matrix(store):
    return np.vstack(list(store.values()))


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    np.random.seed(40)

    mydacc = dacc.mk_dacc()

    healthy = featurizer_store(prefix_filtered_store(mydacc.data, 'Healthy'))
    key_to_tag = lambda x: x.split(os.path.sep)[0]

    tags = Counter((key_to_tag(x) for x in mydacc.data))
    not_healthy_tags = tags.keys() - {'Healthy'}
    not_healthy = featurizer_store(prefix_filtered_store(mydacc.data, not_healthy_tags))

    # from tested import train_test_split_keys
    # train_test_split_keys()

    X_healthy = np.array(list(itertools.chain.from_iterable(healthy.values())))
    y_healthy = ['healthy'] * len(X_healthy)
    X_not_healthy = np.array(list(itertools.chain.from_iterable(not_healthy.values())))
    y_not_healthy = ['not_healthy'] * len(X_not_healthy)

    X = np.vstack([X_healthy, X_not_healthy])
    y = np.hstack([y_healthy, y_not_healthy])

    with mlflow.start_run():
        model = Pipeline(
            steps=[
                ('scale', StandardScaler()),
                ('pca', PCA(n_components=50)),
                ('model', CentroidSmoothing()),
            ]
        )
        model.fit(X, y)
        preds = model.predict(X)
        yy = list(map(int, y == 'healthy'))
        yy_pred = list(map(int, model.predict(X) == 'healthy'))

        f1_res = f1_score(yy, yy_pred)

        mlflow.log_param('chk_size', chk_size)
        mlflow.log_metric('f1_score', f1_res)
        mlflow.sklearn.log_model(
            model, 'model', registered_model_name='CentroidSmoothingModel'
        )
