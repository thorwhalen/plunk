from abc import ABC, abstractmethod
from typing import Any
from utils import IOList, TimestampedData


class IO(ABC):
    def __init__(self, name: str, container: str):
        self.name = name
        self._container = container
        self._connections = IOList(self.matching_type)

    @property
    @abstractmethod
    def matching_type(self) -> type:
        pass

    @property
    def container(self) -> str:
        return self._container

    @property
    def connections(self) -> IOList:
        return self._connections.copy()

    def __str__(self) -> str:
        return f'{self._container}.{self.name}'
        
    def connect(self, obj) -> None:
        self._connections.append(obj)
        obj._connections.append(self)

    def disconnect(self, obj) -> None:
        obj._connections.remove(self)
        self._connections.remove(obj)


class Input(IO):
    pass


class Output(IO):
    pass


class Event(IO):
    def __init__(self, name: str, container: str, on_event: callable = lambda: None):
        super().__init__(name, container)
        self.on_event = on_event
        self._ts = None

    def __repr__(self) -> str:
        return f'{type(self).__name__}' \
            f'({self.name!r}, {self.container!r}, {self.on_event.__qualname__})'
   
    @property
    def ts(self) -> float:
        return self._ts

    def new_event(self, ts: float) -> None:
        self._ts = ts
        self.on_event()


class EventInput(Event, Input):
    @property
    def matching_type(self) -> type:
        return EventOutput


class EventOutput(Event, Output):
    @property
    def matching_type(self) -> type:
        return EventInput

    def new_event(self, ts: float) -> None:
        Event.new_event(self, ts)
        for connection in self._connections:
            connection.new_event(ts)


class Data(IO):
    def __init__(self, name: str, container: str, datatype: type = TimestampedData):
        super().__init__(name, container)
        self._datatype = datatype
        self._value = None

    @property
    def datatype(self) -> type:
        return self._datatype

    @property
    def value(self) -> Any:
        return self._value

    def __repr__(self) -> str:
        return f'{type(self).__name__}' \
            f'({self.name!r}, {self.container!r}, {self.datatype.__qualname__})'

    def connect(self, obj) -> None:
        assert self._datatype == obj._datatype, f'{self} and {obj} have different data types!'
        IO.connect(self, obj)



class DataInput(Data, Input):
    @property
    def matching_type(self) -> type:
        return DataOutput

    def connect(self, obj) -> None:
        assert not self._connections, f'{self} is already connected to {self._connections[0]}!'
        Data.connect(self, obj)

    def pull_data(self) -> None:
        assert self._connections, f'{self} must be connected to a DataOutput object'
        self._value = self._connections[0].value


class DataOutput(Data, Output):
    @property
    def matching_type(self) -> type:
        return DataInput

    @property
    def value(self) -> Any:
        return super().value

    @value.setter
    def value(self, value: Any) -> None:
        if not isinstance(value, self._datatype):
            raise TypeError(f'{self} only accepts {self._datatypes.__name__} values.')
        self._value = value

    def connect(self, obj) -> None:
        DataInput.connect(obj, self)
