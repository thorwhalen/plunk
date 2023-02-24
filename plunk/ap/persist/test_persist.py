from plunk.ap.persist.testing_utilities import mk_step, step_factories
from py2json import Ctor
from plunk.ap.persist.persist import Persist, PersistArgsError


def add(a, b):
    print('add called', f'{a} + {b} = ', end='')
    print(f'{a + b}')

    add.count += 1
    return a + b


add.count = 0


def counter(*_a, **_kw):
    counter.count += 1
    return counter.count - 1


counter.count = 0


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


def test_key_getter_error_handling():

    Persist.any(key_getter=counter, serializer=lambda x: x, store={})
    thrown = False
    try:
        Persist.any(key_getter=counter, serializer=lambda x: x, store=1)
    except PersistArgsError:
        pass
    else:
        raise Exception('Expected PersistArgsError to be raised')

    Persist.serialize_function_call([], {}, counter)
    try:
        Persist.serialize_function_call([], {})
    except PersistArgsError:
        pass
    else:
        raise Exception('Expected PersistArgsError to be raised')

    Persist.serialize_return_value([], {}, return_value=1)
    try:
        Persist.serialize_return_value([], {})
    except PersistArgsError:
        pass
    else:
        raise Exception('Expected PersistArgsError to be raised')


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
        add.count = 0
        serialized = Persist.serialize_function_call(
            a, k, function=add, validate_conversion=True
        )
        print('\nactual      : ', end='')
        actual = add(*a, **k)
        print('deserialized: ', end='')
        deserialized = Persist.deserialize(serialized)

        assert actual == deserialized
        assert add.count == 2, 'add should be called for actual and deserialized'

    print('\nTest Persist.function_call decorator')

    counter.count = 0
    persisted_add = Persist.function_call(
        add, key_getter=counter, store=dict_store, validate_conversion=True
    )
    for i, (a, k) in enumerate(_args_kwargs):
        add.count = 0
        print('\nactual      : ', end='')
        actual = persisted_add(*a, **k)
        serialized = dict_store[i]
        print('deserialized: ', end='')
        deserialized = Persist.deserialize(serialized)

        assert actual == deserialized
        assert add.count == 2, 'add should be called for actual and deserialized'


def test_serialize_return_value():
    _args_kwargs = [
        ((1, 2), {}),
        ((), {'a': 1.3, 'b': 2.6}),
        ((), {'a': list(range(10)), 'b': list(range(10, 20))}),
        ((), {'a': 'hello', 'b': 'world'}),
        ((), {'a': TestClass(1), 'b': TestClass(2)}),
        ((), {'a': TestClass([TestClass(1)]), 'b': TestClass([TestClass(2)])}),
    ]

    print('\nTest Persist.serialize_return_value()')

    for a, k in _args_kwargs:
        add.count = 0
        print('\nactual      : ', end='')
        actual = add(*a, **k)

        serialized = Persist.serialize_return_value(
            return_value=actual, validate_conversion=True
        )
        deserialized = Persist.deserialize(serialized)
        print(f'deserialized: {deserialized}')

        assert actual == deserialized
        assert add.count == 1, 'add should be called only once for actual'

    print('\nTest Persist.return_value decorator')

    counter.count = 0
    persisted_add = Persist.return_value(
        add, key_getter=counter, store=dict_store, validate_conversion=True
    )
    for i, (a, k) in enumerate(_args_kwargs):
        add.count = 0
        print('\nactual      : ', end='')
        actual = persisted_add(*a, **k)
        serialized = dict_store[i]
        deserialized = Persist.deserialize(serialized)
        print(f'deserialized: {deserialized}')

        assert actual == deserialized
        assert add.count == 1, 'add should be called only once for actual'


def test_serialize_chunker():
    from plunk.sb.front_demo.user_story1.apps.app_scrap import Step

    def save_name_getter(args, kwargs, function=None, return_value=None):
        return kwargs['save_name']

    persisted_mk_step = Persist.function_call(
        mk_step, key_getter=save_name_getter, store=dict_store, validate_conversion=True
    )
    chkr = persisted_mk_step(
        step_factory=step_factories['chunker'], kwargs={}, save_name='chkr'
    )
    assert isinstance(chkr, Step), 'Invalid test: Unexpected mk_step output type'

    persisted_chkr = Persist.deserialize(dict_store['chkr'])
    assert isinstance(dict_store['chkr'], str), 'chunker was not serialized'
    assert isinstance(persisted_chkr, Step), 'chunker was not deserialized'


def test_serialize_featurizer():
    from plunk.sb.front_demo.user_story1.apps.app_scrap import Step

    def save_name_getter(args, kwargs, function=None, return_value=None):
        return kwargs['save_name']

    persisted_mk_step = Persist.function_call(
        mk_step, key_getter=save_name_getter, store=dict_store, validate_conversion=True
    )
    feat = persisted_mk_step(
        step_factory=step_factories['featurizer'], kwargs={}, save_name='feat'
    )
    assert isinstance(feat, Step), 'Invalid test: Unexpected mk_step output type'

    persisted_feat = Persist.deserialize(dict_store['feat'])
    assert isinstance(dict_store['feat'], str), 'featurizer was not serialized'
    assert isinstance(persisted_feat, Step), 'featurizer was not deserialized'
