from py2json import Ctor
from plunk.ap.persist.persist import Persist


def add(a, b):
    print(f'{a} + {b} = ', end='')
    print(f'{a + b}')
    return a + b


class TestClass:
    def __init__(self, value):
        self.value = value

    def __add__(self, other: 'TestClass'):
        return TestClass(self.value + other.value)

    def __repr__(self):
        value = self.value
        return f'<{self.__class__.__name__} {value=}>'

    def __eq__(self, other: 'TestClass'):
        return self.to_jdict() == other.to_jdict()

    def to_jdict(self):
        return {'value': self.value}

    @classmethod
    def from_jdict(cls, jdict):
        return TestClass(**jdict)


dict_store = {}


def test_ctor():
    original = TestClass([TestClass(1)])
    print(f'\noriginal    : {original}')
    serialized = Ctor.deconstruct(original)
    deserialized = Ctor.construct(serialized)
    print(f'deserialized: {deserialized}')
    assert original == deserialized


def test_serialize_function_call():
    _args_kwargs = [
        ((1, 2), {}),
        ((), {'a': 1.3, 'b': 2.6}),
        ((), {'a': list(range(10)), 'b': list(range(10, 20))}),
        ((), {'a': 'hello', 'b': 'world'}),
        ((), {'a': TestClass(1), 'b': TestClass(2)}),
        ((), {'a': TestClass([TestClass(1)]), 'b': TestClass([TestClass(2)])}),
    ]

    print('\nTest Persist.serialize_function_call()')

    for a, k in _args_kwargs:
        serialized = Persist.serialize_function_call(
            a, k, function=add, validate_conversion=True
        )
        print('\nactual      : ', end='')
        actual = add(*a, **k)
        print('deserialized: ', end='')
        deserialized = Persist.deserialize(serialized)

        assert actual == deserialized

    print('\nTest Persist.function_call decorator')

    def counter(*args, **kwargs):
        counter.count += 1
        return counter.count - 1

    counter.count = 0

    persisted_add = Persist.function_call(
        add, key_getter=counter, store=dict_store, validate_conversion=True
    )
    for i, (a, k) in enumerate(_args_kwargs):
        print('\nactual      : ', end='')
        actual = persisted_add(*a, **k)
        serialized = dict_store[i]
        print('deserialized: ', end='')
        deserialized = Persist.deserialize(serialized)

        assert actual == deserialized
