import pytest
from plunk.sb.sig_compatibility.sig_builtins import args_for_builtin
from i2 import Sig
from i2.tests.util import sig_to_inputs


def test_dummy():
    assert True


def test_iter():
    func = iter
    args_list = args_for_builtin(iter, prepare_for_Sig=True)
    for item in args_list:
        sig = Sig(item)
        arity = len(item.split(" "))
        inputs = sig_to_inputs(func, argument_vals=[None] * arity)
