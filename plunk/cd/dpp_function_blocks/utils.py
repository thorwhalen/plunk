import math
from typing import Union, Any, Literal, Sequence

class IOList(list):
    def __init__(self, valid_type: type, sequence: Sequence = None):
        self._valid_type = valid_type
        if sequence is not None:
            super().__init__(self._validate_entry(item) for item in sequence)
        else:
            super().__init__()

    @property
    def valid_type(self) -> type:
        return self._valid_type

    def __repr__(self) -> str:
        return f'IOList({self._valid_type.__qualname__}, {super().__repr__()})'

    def __str__(self) -> str:
        str1 = f'{self._valid_type.__name__} list: ['
        str2 = ''.join(f'{obj}, ' for obj in self)[:-2]
        return str1 + str2 + ']'

    def __setitem__(self, pos: int, obj: Any) -> None:
        super().__setitem__(pos, self._validate_entry(obj))

    def print_names_only(self) -> None:
        print('[' + ''.join([f'{obj.name}, ' for obj in self])[:-2] + ']')

    def print_without_container(self) -> None:
        print(f'{self._valid_type.__name__} list:', end=' ')
        self.print_names_only()

    def insert(self, pos: int, obj: Any) -> None:
        super().insert(pos, self._validate_entry(obj))

    def append(self, obj: Any) -> None:
        super().append(self._validate_entry(obj))

    def extend(self, other: Sequence) -> None:
        if isinstance(other, type(self)):
            super().extend(other)
        else:
            super().extend(self._validate_entry(item) for item in other)

    def index_by_name(self, name: str) -> int:
        indices = [ind for ind, io in enumerate(self) if io.name == name]
        if not indices:
            raise ValueError(f'No IO object in this list is named {name}')
        return indices[0]

    def _validate_entry(self, obj: Any) -> Any:
        if not isinstance(obj, self._valid_type):
            raise TypeError(
                f'Cannot insert {type(obj).__name__} object in {self._valid_type.__name__} list!'
            )
        if obj in self:
            raise ValueError(f'{obj} already in {self._valid_type.__name__} list!')
        return obj


class TimestampedData:
    def __init__(self, values: tuple, bt: Union[int, float], tt: Union[int, float]):
        assert bt < tt, 'bt must be lower than tt'
        self._values = values
        self._bt = bt
        self._tt = tt

    @property
    def values(self) -> tuple:
        return self._values

    @property
    def bt(self) -> Union[int, float]:
        return self._bt

    @property
    def tt(self) -> Union[int, float]:
        return self._tt

    def get_ts_of_index(self, ind: int) -> tuple[Union[int, float]]:
        if not 0 <= ind < len(self._values):
            raise IndexError(f'The index must be between 0 and {len(self._values)-1}.')
        bt = self._bt + ind/len(self._values) * (self._tt-self._bt)
        tt = self._bt + (ind+1)/len(self._values) * (self._tt-self._bt)
        return (bt, tt)

    def search_index_prior_to_ts(self, ts: Union[int, float]) -> int:
        return self._search_index_from_ts(ts, 'floor')

    def search_index_next_to_ts(self, ts: Union[int, float]) -> int:
        ind = self._search_index_from_ts(ts, 'ceil')
        if ind == len(self._values):
            raise ValueError(
                'ts is higher than the bt of the last element of the list of values'
            )
        return ind

    def search_index_closest_to_ts(self, ts: Union[int, float]) -> int:
        ind = self._search_index_from_ts(ts, round)
        if ind == len(self._values):
            raise ValueError(
                'ts is closer to tt than to the timestamp of the last element of the list of values'
            )
        return ind

    def _search_index_from_ts(
        self, ts: Union[int, float], rounding_type: Literal['floor', 'ceil'] = 'ceil'
        ) -> int:
        if rounding_type not in ('floor', 'ceil'):
            raise ValueError(
                f'rounding_type must be literal "floor" or "ceil" but got "{rounding_type}"'
            )
        if not self._bt <= ts < self._tt:
            raise ValueError('ts is outside of the timestamp range')
        rounder = getattr(math, rounding_type)
        return rounder((ts-self._bt) / (self._tt-self._bt) * len(self._values))
