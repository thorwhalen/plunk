from typing import Literal, Optional, Callable
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, AppMaker
from front.util import deep_merge
from i2 import name_of_obj

from streamlitfront.elements import FloatSliderInput
from streamlitfront import mk_app
from streamlitfront.spec_maker import SpecMaker
from streamlitfront.tools import (
    OBJECT,
    NAME_OF_OBJ,
    SUBTYPE,
    first_element_matching_type,
)

from operator import attrgetter
from functools import partial


def foo(x: int = 100, p: float = 0.5):
    return x * p


def bar(x: int):
    return x ** 2


foo.front_spec = {'execution': {'inputs': {'p': {ELEMENT_KEY: FloatSliderInput,}},}}

from front.elements import ElementTreeMaker
from itertools import chain


def deep_merge_list(obj, updates):
    for update in updates:
        obj = deep_merge(obj, update)
    return obj


class MyAppMaker(AppMaker):
    def __init__(
        self,
        rules,
        spec_maker_factory: Callable,
        element_tree_maker_factory: Callable = ElementTreeMaker,
    ):
        super().__init__(
            spec_maker_factory=spec_maker_factory,
            element_tree_maker_factory=element_tree_maker_factory,
        )
        self.rules = rules

    def mk_app(self, objs, config=None, convention=None):
        config = config or {}
        config_updates = chain.from_iterable(
            mk_find_render_keys(obj, self.rules) for obj in objs
        )
        config_updates = list(config_updates)
        # print(config_updates)
        config = deep_merge_list(config, config_updates)

        return super().mk_app(objs, config=config, convention=convention)


class OriginalMyAppMaker(AppMaker):
    def mk_app(self, objs, config=None, convention=None):
        config = config or {}
        for obj in objs:
            if hasattr(obj, 'front_spec'):
                obj_config = {
                    RENDERING_KEY: {name_of_obj(obj): obj.front_spec},
                }
                config = deep_merge(config, obj_config)
        return super().mk_app(objs, config=config, convention=convention)


# Valentin: modif made to avoid changing too much right now


# TODO: Extract routing logic (the if/elifs) and expose control to interface
def _find_render_keys(objs, render_keys: dict):
    """Make a static configs that has a one to one relationship with objects"""
    # TODO: raise specific error with more info instead of assert:
    assert set(objs) == set(objs), f"Some of your objects weren't unique"

    for obj in objs:
        if obj in render_keys:
            yield OBJECT, (obj, render_keys[obj])
        elif name_of_obj(obj) in render_keys:
            yield NAME_OF_OBJ, (name_of_obj(obj), render_keys[name_of_obj(obj)])
        elif (
            type_ := first_element_matching_type(
                SUBTYPE, (obj, filter(lambda x: isinstance(x, type), render_keys))
            )
        ) is not None:
            yield type_, name_of_obj(type_)
        else:
            # TODO: More significant error (perhaps list ALL the objects that are not
            #  mapped and suggest what to do about it (given the specific objects and
            #  render keys).
            raise ValueError(f"Object couldn't be mapped to a render_keys key: {obj}")


from typing import TypeVar, Tuple, Iterable, Callable

Obj = TypeVar('Obj')
Output = TypeVar('Output')
Cond = Callable[[Obj], bool]
Then = Callable[[Obj], Output]
Rule = Tuple[Cond, Then]
Rules = Iterable[Rule]

# Note: We could iterate over objs or over rules. Context tells what's best.
# typical use is to define rules and apply to objs like so

# >>> from functools import partial
# >>> singular_find_render_keys = partial(mk_find_render_keys, rules=rules)  # fix rules
# >>> find_render_keys = partial(map, singular_find_render_keys)  # apply to iterable


def mk_find_render_keys(obj: Obj, rules: Rules) -> Iterable[Output]:
    for cond, then in rules:
        if cond(obj):
            yield then(obj)


def alt_mk_find_render_keys(obj: Obj, rules: Rules) -> Iterable[Output]:
    for rule in rules:
        if rule.cond(obj):
            yield rule.then(obj)


def has_metadata(obj: Obj, data='front_spec') -> bool:
    return hasattr(obj, data)


DFLT_COND = partial(has_metadata, data='front_spec')
DFLT_RETRIEVE_SPEC = attrgetter('front_spec')


def config_from_attribute(obj: Obj, retrieve_spec: Callable = DFLT_RETRIEVE_SPEC):
    spec_for_obj = retrieve_spec(obj)
    obj_config = {
        RENDERING_KEY: {name_of_obj(obj): spec_for_obj},
    }

    return obj_config


if __name__ == '__main__':
    rules = [(DFLT_COND, config_from_attribute)]

    app_maker = MyAppMaker(spec_maker_factory=SpecMaker, rules=rules)
    app = app_maker.mk_app([foo, bar], config={APP_KEY: {'title': 'Custom App Maker'}})
    app()
