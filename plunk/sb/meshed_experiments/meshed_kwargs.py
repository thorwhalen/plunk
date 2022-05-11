"""
Investigate a bug found by Christian
kwargs are heavily modified by a dag
"""

from meshed import DAG, FuncNode


def maybe_first(items):
    return items[0] if items else None


def name_of_var_kw_argument(sig):
    var_kw_list = [param.name for param in sig.params if param.kind == VK]
    result = maybe_first(var_kw_list)
    return result


def map_action_on_cond(kvs, cond, expand):
    for k, v in kvs:
        if cond(k):
            yield from expand(v)
        else:
            yield k, v


def flatten_if_var_kw(kvs, var_kw_name):
    cond = lambda k: k == var_kw_name
    expand = lambda k: k.items()

    return map_action_on_cond(kvs, cond, expand)


def kwargs_from_args_and_kwargs(
    self,
    args,
    kwargs,
    *,
    apply_defaults=False,
    allow_partial=False,
    allow_excess=False,
    ignore_kind=False,
    post_process=False,
):
    """Extracts a dict of input argument values for target signature, from args
    and kwargs.

    When you need to manage how the arguments of a function are specified,
    you need to take care of
    multiple cases depending on whether they were specified as positional arguments
    (`args`) or keyword arguments (`kwargs`).

    The `kwargs_from_args_and_kwargs` (and it's sorta-inverse inverse,
    `args_and_kwargs_from_kwargs`)
    are there to help you manage this.

    If you could rely on the the fact that only `kwargs` were given it would
    reduce the complexity of your code.
    This is why we have the `all_pk_signature` function in `signatures.py`.

    We also need to have a means to make a `kwargs` only from the actual `(*args,
    **kwargs)` used at runtime.
    We have `Signature.bind` (and `bind_partial`) for that.

    But these methods will fail if there is extra stuff in the `kwargs`.
    Yet sometimes we'd like to have a `dict` that services several functions that
    will extract their needs from it.

    That's where  `Sig.extract_kwargs(*args, **kwargs)` is needed.
    :param args: The args the function will be called with.
    :param kwargs: The kwargs the function will be called with.
    :param apply_defaults: (bool) Whether to apply signature defaults to the
    non-specified argument names
    :param allow_partial: (bool) True iff you want to allow partial signature
    fulfillment.
    :param allow_excess: (bool) Set to True iff you want to allow extra kwargs
    items to be ignored.
    :param ignore_kind: (bool) Set to True iff you want to ignore the position and
    keyword only kinds,
        in order to be able to accept args and kwargs in such a way that there can
        be cross-over
        (args that are supposed to be keyword only, and kwargs that are supposed
        to be positional only)
    :return: An {argname: argval, ...} dict

    See also the sorta-inverse of this function: args_and_kwargs_from_kwargs

    >>> def foo(w, /, x: float, y="YY", *, z: str = "ZZ"):
    ...     ...
    >>> sig = Sig(foo)
    >>> assert (
    ...     sig.kwargs_from_args_and_kwargs((11, 22, "you"), dict(z="zoo"))
    ...     == sig.kwargs_from_args_and_kwargs((11, 22), dict(y="you", z="zoo"))
    ...     == {"w": 11, "x": 22, "y": "you", "z": "zoo"}
    ... )

    By default, `apply_defaults=False`, which will lead to only get those
    arguments you input.

    >>> sig.kwargs_from_args_and_kwargs(args=(11,), kwargs={"x": 22})
    {'w': 11, 'x': 22}

    But if you specify `apply_defaults=True` non-specified non-require arguments
    will be returned with their defaults:

    >>> sig.kwargs_from_args_and_kwargs(
    ...     args=(11,), kwargs={"x": 22}, apply_defaults=True
    ... )
    {'w': 11, 'x': 22, 'y': 'YY', 'z': 'ZZ'}

    By default, `ignore_excess=False`, so specifying kwargs that are not in the
    signature will lead to an exception.

    >>> sig.kwargs_from_args_and_kwargs(
    ...     args=(11,), kwargs={"x": 22, "not_in_sig": -1}
    ... )
    Traceback (most recent call last):
        ...
    TypeError: Got unexpected keyword arguments: not_in_sig

    Specifying `allow_excess=True` will ignore such excess fields of kwargs.
    This is useful when you want to source several functions from a same dict.

    >>> sig.kwargs_from_args_and_kwargs(
    ...     args=(11,), kwargs={"x": 22, "not_in_sig": -1}, allow_excess=True
    ... )
    {'w': 11, 'x': 22}

    On the other side of `ignore_excess` you have `allow_partial` that will allow
    you, if
    set to `True`, to underspecify the params of a function (in view of being
    completed later).

    >>> sig.kwargs_from_args_and_kwargs(args=(), kwargs={"x": 22})
    Traceback (most recent call last):
      ...
    TypeError: missing a required argument: 'w'

    But if you specify `allow_partial=True`...

    >>> sig.kwargs_from_args_and_kwargs(
    ...     args=(), kwargs={"x": 22}, allow_partial=True
    ... )
    {'x': 22}

    That's a lot of control (eight combinations total), but not everything is
    controllable here:
    Position only and keyword only kinds need to be respected:

    >>> sig.kwargs_from_args_and_kwargs(args=(1, 2, 3, 4), kwargs={})
    Traceback (most recent call last):
      ...
    TypeError: too many positional arguments
    >>> sig.kwargs_from_args_and_kwargs(args=(), kwargs=dict(w=1, x=2, y=3, z=4))
    Traceback (most recent call last):
      ...
    TypeError: 'w' parameter is positional only, but was passed as a keyword

    But if you want to ignore the kind of parameter, just say so:

    >>> sig.kwargs_from_args_and_kwargs(
    ...     args=(1, 2, 3, 4), kwargs={}, ignore_kind=True
    ... )
    {'w': 1, 'x': 2, 'y': 3, 'z': 4}
    >>> sig.kwargs_from_args_and_kwargs(
    ...     args=(), kwargs=dict(w=1, x=2, y=3, z=4), ignore_kind=True
    ... )
    {'w': 1, 'x': 2, 'y': 3, 'z': 4}
    """
    no_var_kw = not self.has_var_keyword
    # no_var_kw = True

    if ignore_kind:
        sig = self.normalize_kind(
            # except_kinds=frozenset()
        )
    else:
        sig = self

    # no_var_kw = not sig.has_var_keyword TODOD check this
    if no_var_kw:  # has no var keyword kinds
        sig_relevant_kwargs = {
            name: kwargs[name] for name in sig if name in kwargs
        }  # take only what you need
    else:
        sig_relevant_kwargs = kwargs  # take all the kwargs
    binder = sig.bind_partial if allow_partial else sig.bind
    if not self.has_var_positional and allow_excess:
        max_allowed_num_of_posisional_args = sum(k <= PK for k in self.kinds.values())
        args = args[:max_allowed_num_of_posisional_args]

    b = binder(*args, **sig_relevant_kwargs)
    if apply_defaults:
        b.apply_defaults()

    if no_var_kw and not allow_excess:  # don't ignore excess kwargs
        excess = kwargs.keys() - b.arguments
        if excess:
            excess_str = ", ".join(excess)
            raise TypeError(f"Got unexpected keyword arguments: {excess_str}")

    if post_process:
        var_kw_name = name_of_var_kw_argument(self)

        kvs = b.arguments.items()

        flattened_kvs = flatten_if_var_kw(kvs, var_kw_name)
        result = dict(flattened_kvs)

    else:
        result = b.arguments
    return result


if __name__ == "__main__":

    # def f(a, **kwargs):
    #    print(kwargs)
    #    return a

    # f_node = FuncNode(func=f)
    # d = DAG([f_node])  # breakpoint
    # args = ['a'=1]
    # kwargs = {'x'=3}

    # d(*args, **kwargs
    # scope = d.sig.kwargs_from_args_and_kwargs((), {"a": 1, "x": 3})
    # assert scope == {"a": 1, "kwargs": {"x": 3}}
    # d.call_on_scope(scope)  # breakpoint
    # assert scope == {"a": 1, "kwargs": {"x": 3}, "f": 1}
    # res = d.extract_output_from_scope(scope, d.leafs)

    # print(res)  # breakpoint
    from i2 import Sig
    from i2.signatures import VK

    def foo(w, /, x: float, y="YY", *, z: str = "ZZ", **rest):
        pass

    sig = Sig(foo)
    res = kwargs_from_args_and_kwargs(
        sig, (11, 22, "you"), dict(z="zoo", other="stuff"), post_process=True
    )
    assert res == {"w": 11, "x": 22, "y": "you", "z": "zoo", "other": "stuff"}
