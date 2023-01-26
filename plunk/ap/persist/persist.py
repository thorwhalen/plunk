import json
from dataclasses import dataclass
from functools import wraps
from typing import Protocol, runtime_checkable, Hashable, Any, Union

from py2json import Ctor
from py2json.ctor import classproperty

Serialized = Union[bytes, str]


@runtime_checkable
class KeyGetter(Protocol):
    def __call__(self, args, kwargs, function=None, return_value=None) -> Hashable:
        ...


@runtime_checkable
class Serializer(Protocol):
    def __call__(self, args, kwargs, function=None, return_value=None) -> Serialized:
        ...


@runtime_checkable
class Deserializer(Protocol):
    def __call__(self, serialized: Serialized) -> Any:
        ...


@runtime_checkable
class Store(Protocol):
    def __setitem__(self, key, value):
        ...


class Persist:
    ctor: Ctor = Ctor

    @classmethod
    def any(
        cls, func=None, *, key_getter: KeyGetter, serializer: Serializer, store: Store,
    ) -> Any:
        def _decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                _rv = f(*args, **kwargs)
                _key = key_getter(args, kwargs, return_value=_rv, function=f)
                _val = serializer(args, kwargs, return_value=_rv, function=f)
                store[_key] = _val
                return _rv

            return wrapped

        return _decorator(func) if callable(func) else _decorator

    @classmethod
    def function_call(
        cls, func=None, *, key_getter: KeyGetter = None, store=None
    ) -> Any:
        return cls.any(
            func,
            key_getter=key_getter,
            serializer=cls.serialize_function_call,
            store=store,
        )

    @classmethod
    def serialize_function_call(
        cls, args, kwargs, function, return_value=None,
    ) -> Serialized:
        _a = cls.ctor.deconstruct(args)
        _kw = cls.ctor.deconstruct(kwargs)
        ctor_dict = cls.ctor.to_ctor_dict(constructor=function, args=_a, kwargs=_kw)
        jdict = cls.ctor.to_jdict(ctor_dict)
        return json.dumps(jdict)

    @classmethod
    def deserialize(cls, serialized: Serialized):
        jdict = json.loads(serialized)
        return cls.ctor.construct(jdict)

    def _default_key_getter(self):
        pass
