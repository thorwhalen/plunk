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
    def __call__(
        self,
        args=None,
        kwargs=None,
        function=None,
        return_value=None,
        validate_conversion=False,
    ) -> Serialized:
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
        cls,
        func=None,
        *,
        key_getter: KeyGetter,
        serializer: Serializer,
        store: Store,
        validate_conversion=False,
    ) -> Any:
        def _decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                _rv = f(*args, **kwargs)
                _key = key_getter(args, kwargs, return_value=_rv, function=f)
                _val = serializer(
                    args=args,
                    kwargs=kwargs,
                    return_value=_rv,
                    function=f,
                    validate_conversion=validate_conversion,
                )
                store[_key] = _val
                return _rv

            return wrapped

        return _decorator(func) if callable(func) else _decorator

    @classmethod
    def function_call(
        cls,
        func=None,
        *,
        key_getter: KeyGetter = None,
        store=None,
        validate_conversion=False,
    ) -> Any:
        """Function decorator to serialize function, args, and kwargs

        :param func:
        :param key_getter:
        :param store:
        :param validate_conversion:
        :return:
        """

        return cls.any(
            func,
            key_getter=key_getter,
            serializer=cls.serialize_function_call,
            store=store,
            validate_conversion=validate_conversion,
        )

    @classmethod
    def serialize_function_call(
        cls, args, kwargs, function, return_value=None, validate_conversion=False
    ) -> Serialized:
        """Serializer method

        :param args:
        :param kwargs:
        :param function:
        :param return_value: N/A
        :param validate_conversion:
        :return:
        """
        _a = cls.ctor.deconstruct(args, validate_conversion)
        _kw = cls.ctor.deconstruct(kwargs, validate_conversion)
        ctor_dict = cls.ctor.to_ctor_dict(constructor=function, args=_a, kwargs=_kw)
        jdict = cls.ctor.to_jdict(ctor_dict)
        return json.dumps(jdict)

    @classmethod
    def return_value(
        cls,
        func=None,
        *,
        key_getter: KeyGetter = None,
        store=None,
        validate_conversion=False,
    ) -> Any:
        """Function decorator to serialize the return value of the function

        :param func:
        :param key_getter:
        :param store:
        :param validate_conversion:
        :return:
        """

        return cls.any(
            func,
            key_getter=key_getter,
            serializer=cls.serialize_function_call,
            store=store,
            validate_conversion=validate_conversion,
        )

    @classmethod
    def serialize_return_value(
        cls,
        args=None,
        kwargs=None,
        function=None,
        return_value=None,
        validate_conversion=False,
    ) -> Serialized:
        """Serializer method

        :param args: N/A
        :param kwargs: N/A
        :param function: N/A
        :param return_value:
        :param validate_conversion:
        :return:
        """
        ctor_jdict = cls.ctor.deconstruct(return_value, validate_conversion)
        return json.dumps(ctor_jdict)

    @classmethod
    def deserialize(cls, serialized: Serialized):
        jdict = json.loads(serialized)
        return cls.ctor.construct(jdict)

    def _default_key_getter(self):
        pass
