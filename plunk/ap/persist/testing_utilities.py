from functools import partial
from typing import Callable

from front import Crudifier
from i2 import FuncFactory
from plunk.sb.front_demo.user_story1.apps.app_scrap import Step
from plunk.sb.front_demo.user_story1.utils.tools import (
    clean_dict,
    simple_chunker,
    simple_featurizer,
)

mall = {'steps': {}}

crudifier = partial(Crudifier, mall=mall)

step_factories = {
    'chunker': FuncFactory(simple_chunker),
    'featurizer': FuncFactory(simple_featurizer),
}


@crudifier(output_store='steps')
def mk_step(step_factory: Callable, kwargs: dict):
    kwargs = clean_dict(kwargs)
    step = partial(step_factory, **kwargs)()
    result = Step(step=step, step_factory=step_factory)
    return result
