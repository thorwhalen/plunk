import builtins
import types
from typing import Iterable
from i2 import Sig


def get_builtin_function_types():
    builtin_function_names = [
        name
        for name, obj in vars(builtins).items()
        if isinstance(obj, types.BuiltinFunctionType)
    ]
    return builtin_function_names


def get_lines_from_string(text):
    return text.split("\n")


def extract_doc(doc):
    lines = get_lines_from_string(doc)
    result = []  # better: yield and do list()
    for line in lines:
        if line.strip():
            result.append(line)
        else:
            break
    return result


def enclosed_text(text):
    idx1 = text.find("(")
    idx2 = text.find(")", idx1)

    if idx1 != -1 and idx2 != -1 and (idx2 > idx1 + 1):
        result = text[idx1 + 1 : idx2]
    return result


def args_for_builtin(builtin_func, prepare_for_Sig=False):
    """Extract the args from builtin doc"""

    docstr = builtin_func.__doc__
    doc = extract_doc(docstr)
    name = builtin_func.__name__

    result = []
    for line in doc:
        s = line.replace(name, "", 1)
        args = enclosed_text(s)
        if prepare_for_Sig:
            args = args.replace(",", "")
        result.append(args)

    return result


def args_str_from_sig(sig):
    return str(sig)[1:-1]


def sig_to_lambda(sig):
    args = args_str_from_sig(sig)
    lambda_func = eval(f"lambda {args}:  None")
    return lambda_func


def builtin_func_from_name(name, names_dict):
    sig = Sig(names_dict[name])

    # func = sig_to_func(name, names_dict)
    func = sig_to_lambda(sig)

    return func


def sig_to_func(name, names_dict):
    sig = Sig(names_dict[name])

    args = args_str_from_sig(sig)
    # exec(f"global foo_{name}")
    exec(f"global foo_{name}\n\ndef foo_{name}({args}):\n  return None")
    func = eval(f"global foo_{name}")
    return func
