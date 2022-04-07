import pytest
from typing import List, Dict, Callable, Iterable
from plunk.sb.type_compatibility.compatible import has_compatible_type, builtins


def test_builtins_leaves():

    assert has_compatible_type(int, float)
    assert has_compatible_type(int, int)
    assert has_compatible_type(List[int], List[float])

    assert not has_compatible_type(List[float], List[int])
    assert has_compatible_type(Dict[str, List[int]], Dict[str, List[float]])
