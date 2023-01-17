from typing import Literal, Optional
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, AppMaker
from front.util import deep_merge
from i2 import name_of_obj

from streamlitfront.elements import FloatSliderInput
from streamlitfront import mk_app
from streamlitfront.spec_maker import SpecMaker


def foo(x: int = 100, p: float = 0.5):
    return x * p


foo.front_spec = {
    'execution': {'inputs': {'p': {ELEMENT_KEY: FloatSliderInput,}},}
}


class MyAppMaker(AppMaker):
    def mk_app(self, objs, config = None, convention = None):
        config = config or {}
        for obj in objs:
            if hasattr(obj, 'front_spec'):
                obj_config = {
                    RENDERING_KEY: {
                        name_of_obj(obj): obj.front_spec
                    },
                }
                config = deep_merge(config, obj_config)
        return super().mk_app(objs, config=config, convention=convention)


if __name__ == '__main__':

    app_maker = MyAppMaker(spec_maker_factory=SpecMaker)
    app = app_maker.mk_app(
        [foo],
        config={APP_KEY: {'title': 'Custom App Maker'}}
    )
    app()
