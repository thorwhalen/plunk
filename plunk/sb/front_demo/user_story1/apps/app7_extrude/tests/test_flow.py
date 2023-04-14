from urllib.parse import urljoin
import pytest
from http2py import HttpClient

from platform_poc.apps.web_service.app import API_URL
from platform_poc.tests.data import get_data
from platform_poc import features

from platform_poc.data import mall
from functools import partial
from front.crude import prepare_for_crude_dispatch
import uuid
import time
import pandas as pd


def retrieve_data(sref):
    import soundfile as sf
    import os

    home_directory = os.path.expanduser("~")
    path = os.path.join(home_directory + "/Dropbox/OtoSense/VacuumEdgeImpulse/", sref)

    arr = sf.read(path, dtype="int16")[0]
    return path, arr


DFLT_FPATH = "../data/mock_data.csv"


def mk_dataset() -> pd.DataFrame:
    df = pd.read_csv(DFLT_FPATH)
    return df


MOCK_SESSIONS = mk_dataset()

crudifier = partial(
    prepare_for_crude_dispatch, mall=mall, include_stores_attribute=True
)


@crudifier(
    output_store="sessions",
    auto_namer=lambda: str(uuid.uuid4()),
    output_trans=lambda: None,
)
def generate_session():
    return mk_dataset()


@pytest.mark.parametrize(
    "source",
    [features]
    # , lambda: HttpClient(url=urljoin(API_URL, "openapi"))],
)
def test_flow(source):
    # I need to do this trick because the fixtures are not ready when the program
    # computes the parameters in `pytest.mark.parametrize`.
    if callable(source):
        source = source()
    sessions = generate_session()
    training_data = list(get_data("training", 50))
    testing_data = list(get_data("testing", 50))

    # Load data
    source.upload_audio_data(
        audio_data=training_data, tag="training", save_name="my_training_data"
    )
    source.upload_audio_data(
        audio_data=testing_data, tag="testing", save_name="my_testing_data"
    )
    assert True
