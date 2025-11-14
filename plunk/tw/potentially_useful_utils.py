# --------------------------------------------------------------------------------

# Note: I meant to use this to enable url values of mappings to carry more information.
#  For now I am solving the need differently.
class StringWhereYouCanAddAttrs(str):
    """A ``str``, but with the ability to add attributes to it.

    >>> s = StringWhereYouCanAddAttrs('hello')
    >>> s
    'hello'
    >>> isinstance(s, str)
    True

    Okay, just like a string, but we couldn't do the following with a str:

    >>> s.foo = 'baz'
    >>> s.foo
    'baz'
    >>> s.new_attr = 42
    >>> s.new_attr
    42

    """

    def __setattr__(self, key, value):
        if key in dir(str):
            raise AttributeError(
                f"Can't set attribute {key} on a a StrWithAttributes instance since "
                f'it is already an attribute of builtin str.'
            )
        super().__setattr__(key, value)


# --------------------------------------------------------------------------------
