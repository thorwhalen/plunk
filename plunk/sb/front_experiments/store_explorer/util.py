from functools import reduce  # forward compatibility for Python 3
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
    res = []

    for key, value in d.items():
        res.append([str(key)])
        if isinstance(value, dict):
            res += [[str(key)] + item for item in get_all_path_keys(value)]
    return res


if __name__ == "__main__":
    dataDict = {
        "a": {"r": 1, "s": 2, "t": 3},
        "b": {"u": 1, "v": {"x": 1, "y": 2, "z": 3}, "w": 3},
    }

    assert get_by_path(dataDict, ["a", "r"]) == 1

    assert get_by_path(dataDict, ["b", "v", "y"]) == 2

    d = {"dict1": {"foo": 1, "bar": 2}, "dict2": {"dict3": {"baz": 3, "quux": 4}}}
    for x in get_all_path_keys(d):
        print(x)
