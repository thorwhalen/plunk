import pytest
from plunk.sb.sig_compatibility.sig_builtins import args_for_builtin
from i2 import Sig
from i2.tests.util import sig_to_inputs

from typing import Iterable, Iterator, Callable
from i2.signatures import dict_of_attribute_signatures


@dict_of_attribute_signatures
class names:
    def bool(x) -> bool:
        ...

    def breakpoint(*args, **kwargs):
        ...

    def bytearray(iterable_of_ints: Iterable[int]):
        ...

    def bytes(string: str, encoding=None, errors=None):
        ...

    def classmethod(function: Callable):
        ...

    def dict(**kwargs):
        ...

    def frozenset(iterable: Iterable = None):
        ...

    def int(x, base=10):
        ...

    def iter(callable: Callable, sentinel=None):
        ...

    def max(*args, **keywords):
        ...

    def min(*args, **keywords):
        ...

    def next(iterator: Iterator, default=None):
        ...

    def range(stop):
        ...  # TODO treat range(start, stop)

    def set(iterable: Iterable = None):
        ...

    # def slice(start = None, stop, step=None):...  #TODO !!
    def staticmethod(function: Callable):
        ...

    def str(bytes_or_buffer, encoding=None, errors=None):
        ...

    def super(type_, obj=None):
        ...

    def type(name, bases=None, dict=None):
        ...

    def vars(*obj):
        ...

    def zip(*iterables: Iterable):
        ...


def is_valid_call(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        return True
    except ValueError:
        return False


def builtin_func_from_name(name):
    sig = Sig(names[name])

    @sig
    def f(*args, **kwargs):
        return args, kwargs

    return f


def test_bool():
    name = "bool"

    f = builtin_func_from_name(name)
    assert is_valid_call(f, "12")
    assert is_valid_call(f, 5)


def test_breakpoint():
    name = "breakpoint"
    sig = Sig(names[name])
    inputs = sig_to_inputs(sig)
    # f = builtin_func_from_name(name)
    # assert is_valid_call(f, "12")
    # assert is_valid_call(f, 5)
