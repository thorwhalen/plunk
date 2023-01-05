from streamlitfront.examples import simple_ml_1 as sml
from know.boxes import *
from streamlitfront.elements import FileUploader
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from streamlitfront import mk_app, binder as b
from typing import Mapping
from dol import Pipe
from operator import methodcaller
from pathlib import Path
import numpy as np
from recode import decode_wav_bytes
from plunk.sb.front_demo.user_story1.components.components import ArrayPlotter
from i2 import Sig
from front.dag import crudify_funcs
from meshed import code_to_dag

from plunk.sb.front_demo.user_story1.utils.funcs import (
    learn_apply_model,
    upload_sound,
)
from streamlitfront.elements import SelectBox
from dataclasses import dataclass
import streamlit as st


@dataclass
class MyClass:
    z: int


def func(x: int, y=3, z=None, other=MyClass(z=3)):
    return type(other)


if __name__ == '__main__':

    app = mk_app([func])

    app()
