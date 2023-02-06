import math
from dataclasses import dataclass
from typing import Any

from dol import wrap_kvs


@dataclass
class ItemGetter:
    """Wraps value in a callable to be retrieved later"""

    instance: Any
    key: Any

    def __call__(self):
        return self.instance[self.key]


wrap_kvs_as_square_data = wrap_kvs(data_of_obj=lambda x: x * x, obj_of_data=math.sqrt)


@wrap_kvs_as_square_data
class DoubleWrapSquareStore(dict):
    def item_getter(self, key) -> ItemGetter:
        """The instance self has wrap_kvs applied again to retain the data conversion"""
        return ItemGetter(instance=wrap_kvs_as_square_data(self), key=key)


@wrap_kvs_as_square_data
class SingleWrapSquareStore(dict):
    def item_getter(self, key) -> ItemGetter:
        """The instance self does not have wrap_kvs reapplied and does not act like the instance"""
        return ItemGetter(instance=self, key=key)


def test_square_store(ss):
    ss['2'] = 2
    ig_from_instance = ItemGetter(ss, '2')()
    ig_from_self = ss.item_getter('2')()

    print(
        f'\nTesting {type(ss).__name__}' 'These values should be equal:',
        f"{ss['2']=}",
        f'{ig_from_instance=}',
        f'{ig_from_self=}',
        sep='\n',
    )

    assert (
        ss['2'] == ig_from_instance
    ), f'{type(ss).__name__}: ItemGetter value from instance does not match actual value'

    ig_2 = ss.item_getter('2')
    assert (
        ss['2'] == ig_from_self
    ), f'{type(ss).__name__}: ItemGetter value from self does not match actual value'

    assert (
        ig_from_instance == ig_from_self
    ), f'{type(ss).__name__}: ItemGetter value from instance does not match ItemGetter value from self'


test_square_store(DoubleWrapSquareStore())
test_square_store(SingleWrapSquareStore())
