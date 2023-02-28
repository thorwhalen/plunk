
# --------------------------------------------------------------------------------

from collections import UserString


# Note: I meant to use this to enable url values of mappings to carry more information.
#  For now I am solving the need differently.
class StrWithAttributes(UserString, str):
    """Adds the ability to have strings with attributes.

    >>> s = StrWithAttributes('hello', foo='bar')
    >>> s
    'hello'
    >>> s.foo
    'bar'
    >>> s.foo = 'baz'
    >>> s.foo
    'baz'
    >>> s.new_attr = 42
    >>> s.new_attr
    42
    >>> isinstance(s, str)
    True

    """
    def __init__(self, string, **attributes):
        super().__init__(string)
        clashing_attrs = attributes.keys() & dir(str)
        assert not clashing_attrs, f"These names clash with str attributes: {clashing_attrs}"
        for attr_name, attr_val in attributes.items():
            setattr(self, attr_name, attr_val)


# --------------------------------------------------------------------------------