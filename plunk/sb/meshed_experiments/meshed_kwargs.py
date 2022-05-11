"""
Investigate a bug found by Christian
kwargs are heavily modified by a dag
"""

from meshed import DAG, FuncNode


def f(a, **kwargs):
    print(kwargs)
    return a


if __name__ == "__main__":
    f_node = FuncNode(func=f)
    d = DAG([f_node])  # breakpoint
    # args = ['a'=1]
    # kwargs = {'x'=3}

    # d(*args, **kwargs
    scope = d.sig.kwargs_from_args_and_kwargs((), {"a": 1, "x": 3})
    assert scope == {"a": 1, "kwargs": {"x": 3}}
    # d.call_on_scope(scope)  # breakpoint
    # assert scope == {"a": 1, "kwargs": {"x": 3}, "f": 1}
    # res = d.extract_output_from_scope(scope, d.leafs)

    # print(res)  # breakpoint
