from pytest import fixture


from hypothesis import given, strategies as st


@given(st.integers(3), st.integers(3))
def test_ints_are_commutative(x, y):
    assert x + y == y + x


def test():
    assert True
