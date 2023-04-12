from plunk.sb.front_demo.user_story1.apps.app8_extrude.data.mall import mall
from i2 import Sig


def get_step_factory_sig(step_name):
    step = mall["steps"].get(step_name)
    return Sig(step.step_factory)


def get_pipeline(pipeline_name):
    pipe = mall["pipelines"].get(pipeline_name)
    return pipe
