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
