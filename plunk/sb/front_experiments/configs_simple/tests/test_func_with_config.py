import pytest
from plunk.sb.front_experiments.configs_simple.func_with_config import (
    FuncWithConfigs,
    process_func,
    todict,
)
from front import ELEMENT_KEY
from streamlitfront.elements import FileUploader
from streamlitfront.elements import SuccessNotification
from pytest import fixture
from plunk.sb.front_demo.user_story1.utils.funcs import upload_sound


def test_dummy():
    assert True


@fixture
def sample_func():
    def foo(x: int):
        return x + 1

    upload_component = FuncWithConfigs(
        func=foo,
        overwrite={
            "execution.inputs.train_audio": {
                ELEMENT_KEY: FileUploader,
                "type": "wav",
                "accept_multiple_files": True,
            },
        },
    )
    return upload_component


@fixture
def sample_config_dict():
    return {
        "foo": {
            "execution": {
                "inputs": {
                    "train_audio": {
                        "_front_element": FileUploader,
                        "accept_multiple_files": True,
                        "type": "wav",
                    }
                },
                "output": {"_front_element": SuccessNotification},
            }
        }
    }


def test_func(sample_func, sample_config_dict):

    assert sample_func() == sample_config_dict


def test_process_func(sample_func, sample_config_dict):
    _, config = process_func(sample_func)
    assert config == sample_config_dict


# at least 2 such funcs
# gather their configs into a single config
# pass it to mk_app([funcs], config)
# ([component], config, convention)--> mk_specs--> (new_funcs, config_updated, convention) --> mk_app
# assume 1-1 correspondance between new_funcs and configs (given that: ask make app to verify it)
