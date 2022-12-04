from dataclasses import dataclass
from typing import Callable, Dict
from front import ELEMENT_KEY
from streamlitfront.elements import SuccessNotification
from i2 import Sig
from streamlitfront.elements import FileUploader
from dol.paths import KeyPath
from collections import defaultdict


def merge_dicts(d1, d2):
    return {**d1, **d2}


def overwrite_dict(d1, d2):
    for key, val in d2.items():
        # print(f"{key=}, {val=}")
        d1[key] = val
    return d1


dflt_template = defaultdict(
    dict,
    {
        'execution': {
            # "inputs": dict(),
            'output': {ELEMENT_KEY: SuccessNotification,},
        },
    },
)


@dataclass
class Component:  # more like preferences
    func: Callable
    label: str = None
    # param_to_mall_map: Dict[str, str] = ()
    # output_store_name: str = None

    @property
    def configs(self):
        s = dflt_template
        sig = Sig(self.func)

        # s["execution"]["inputs"] = {arg_name: dict() for arg_name in sig.names}

        s = KeyPath('.')(s)

        return s

    def mk_configs(
        self, overwrites
    ):  # use may be the keypath here only for the overwrites
        # might need to cast the overwrites and also the output to keypath
        # overwrites  = KeyPath('.')(overwrites)
        result = KeyPath('.')(merge_dicts(self.configs, overwrites))
        return result

    __call__ = mk_configs


if __name__ == '__main__':
    from plunk.sb.front_demo.user_story1.utils.funcs import upload_sound

    upload_component = Component(func=upload_sound)
    print(upload_component.configs)
    result = upload_component.mk_configs(
        {
            'execution.inputs.train_audio': {
                ELEMENT_KEY: FileUploader,
                'type': 'wav',
                'accept_multiple_files': True,
            },
        }
    )
    # print(upload_component.configs)
    print(result)
