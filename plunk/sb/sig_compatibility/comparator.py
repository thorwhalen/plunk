from i2 import Sig


def matcher_by_index(sig1, sig2: Sig):
    from itertools import zip_longest

    result = list(zip_longest(sig1.params, sig2.params, fillvalue=None))
    min_length = min(len(sig1), len(sig2))

    return result[:min_length], result[min_length:]


if __name__ == '__main__':
    sig1 = Sig('x y z')
    sig2 = Sig('a b')
#     result = matcher_by_index(sig1, sig2)
#     expected = ([(<Param "x">, <Param "a">), (<Param "y">, <Param "b">)],
#  [(<Param "z">, None)])
#     assert result == expected
