"""An app that loads wav file from local folder"""
from typing import Mapping
from functools import partial
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY

from front.crude import Crudifier

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import SuccessNotification, SelectBox
from streamlitfront.elements import FileUploader

from plunk.ap.store_explorer.store_explorer_element import StoreExplorer


def mk_pipeline_maker_app_with_mall(mall: Mapping,):
    if not b.mall():
        b.mall = mall
    mall = b.mall()

    crudifier = partial(Crudifier, mall=mall)

    @crudifier(output_store='sound_output')
    def upload_sound(train_audio: list, tag: str):
        return train_audio, tag

    def explore_mall(key):
        return mall[key]

    config = {
        APP_KEY: {'title': 'Data Preparation'},
        RENDERING_KEY: {
            'upload_sound': {
                # NAME_KEY: "Data Loader",
                'execution': {
                    'inputs': {
                        'train_audio': {
                            ELEMENT_KEY: FileUploader,
                            'type': 'wav',
                            'accept_multiple_files': True,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'Wav files loaded successfully.',
                    },
                },
            },
            'explore_mall': {
                'execution': {
                    'inputs': {'key': {ELEMENT_KEY: SelectBox, 'options': list(mall)}},
                    'output': {ELEMENT_KEY: StoreExplorer},
                }
            },
        },
    }

    funcs = [
        explore_mall,
        upload_sound,
    ]
    app = mk_app(funcs, config=config)

    return app


mall = dict(
    # Factory Input Stores
    sound_output=dict(),
    # Output Store
    data=dict(
        a=1,
        b='2',
        c=[3],
        d={'4': 4, '5': [{'e': 6}, {'f': 7}, ['g', 'h', 'i']]},
        j=[{'k': 8, 'l': 9}, 'm', 10],
    ),
)


if __name__ == '__main__':

    app = mk_pipeline_maker_app_with_mall(mall)

    app()
