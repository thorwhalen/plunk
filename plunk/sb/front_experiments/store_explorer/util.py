from functools import reduce
import operator


def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)


def set_by_path(root, items, value):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(root, items[:-1])[items[-1]] = value


def del_by_path(root, items):
    """Delete a key-value in a nested object in root by item sequence."""
    del get_by_path(root, items[:-1])[items[-1]]


def get_all_path_keys(d):
    for key, value in d.items():
        yield [key]
        if isinstance(value, dict):
            yield from [[key] + item for item in get_all_path_keys(value)]


# from boltons.iterutils import remap

# def get_all_keys(d):
#     res = []
#     def append_keys(path, key, value):
#         res.append(list(path)+[key])
#         return key, value
#     remap(d, visit=append_keys)
#     return res


if __name__ == "__main__":
    dataDict = {
        "a": {"r": 1, "s": 2, "t": 3},
        "b": {"u": 1, "v": {"x": 1, "y": 2, "z": 3}, "w": 3},
    }

    assert get_by_path(dataDict, ["a", "r"]) == 1

    assert get_by_path(dataDict, ["b", "v", "y"]) == 2

    d = {"dict1": {"foo": 1, "bar": 2}, "dict2": {"dict3": {"baz": 3, "quux": 4}}}

    print(list(get_all_path_keys(d)))
