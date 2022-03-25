import pytest
from pytest import fixture
from i2 import Sig


def test_sig_to_func():
    sig = Sig("a b")
