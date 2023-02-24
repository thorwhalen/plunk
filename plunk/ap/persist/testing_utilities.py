from functools import partial
from typing import Callable, Iterable, List

from front import Crudifier
from i2 import FuncFactory
from lined import LineParametrized
from plunk.sb.front_demo.user_story1.apps.app_scrap import Step, Pipeline
from plunk.sb.front_demo.user_story1.utils.tools import (
    clean_dict,
    simple_chunker,
    simple_featurizer,
)

mall = {'steps': {}, 'pipelines': {}}

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


def get_step_name(step: Step) -> str:
    return [k for k, v in mall['steps'].items() if v.step == step][0]


@crudifier(output_store='pipelines')
def mk_pipeline(steps: List[Step]):
    named_funcs = [(get_step_name(step), step) for step in steps]
    pipeline = Pipeline(steps=steps, pipe=LineParametrized(*named_funcs))
    return pipeline
