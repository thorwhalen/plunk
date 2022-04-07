from typing import List, Dict, Iterable, Callable

builtins = [int, float, str, bool]


def has_compatible_type(typing_inst1, typing_inst2):
    # types are compatible if equal
    if typing_inst1 == typing_inst2:
        return True

    # treat the builtins separately
    if typing_inst1 == int and typing_inst2 == float:
        return True
    if typing_inst1 == List and typing_inst2 == Iterable:
        return True
    if (
        typing_inst1 in builtins
        and typing_inst2 in builtins
        and typing_inst1 != typing_inst2
    ):
        return False

    # split into root and leaves
    origin1, args1 = typing.get_origin(typing_inst1), typing.get_args(typing_inst1)
    origin2, args2 = typing.get_origin(typing_inst2), typing.get_args(typing_inst2)

    # roots must be compatible
    origin_comp = has_compatible_type(origin1, origin2)

    # args in the leaves must have equal numbers
    len_comp = len(args1) == len(args2)

    # corresponding args must be compatible
    args_comp = all(
        [has_compatible_type(arg1, arg2) for arg1, arg2 in zip(args1, args2)]
    )

    return origin_comp and len_comp and args_comp
