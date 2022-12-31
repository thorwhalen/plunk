from io import BytesIO
from typing import Callable
import streamlit as st
import soundfile as sf
import matplotlib.pyplot as plt
from extrude import mk_web_app
from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
from front.elements import OutputBase
from streamlitfront.elements import (
    AudioRecorder,
    FileUploader,
    MultiSourceInput,
    SuccessNotification,
    TextInput,
)

from plunk.vf.extrude.edge_impulse_like import funcs
from plunk.vf.extrude.edge_impulse_like.api import api_url


class FileReader(FileUploader):
    def render(self):
        uploaded_file = super().render()
        if uploaded_file:
            data = uploaded_file.getvalue()
            print(data)
            print(type(data))
            return data


class AudioPlayer(OutputBase):
    def render(self):
        if self.output:
            # wf = self.output['wf'].encode()
            # tag = self.output['tag']
            wf = self.output
            arr = sf.read(BytesIO(wf), dtype='int16')[0]
            tab1, tab2 = st.tabs(['Audio Player', 'Waveform'])
            with tab1:
                st.audio(wf)
            with tab2:
                # label = f'Tag={tag}'
                label = 'Plot'
                fig, ax = plt.subplots(figsize=(15, 5))
                ax.plot(arr, label=f'Tag={label}')
                ax.legend()
                st.pyplot(fig)


if __name__ == '__main__':
    app = mk_web_app(
        funcs,
        api_url=api_url,
        config={
            APP_KEY: {'title': 'Edge-Impulse-like App'},
            RENDERING_KEY: {
                'upload_data': {
                    'execution': {
                        'inputs': {
                            'x': {
                                ELEMENT_KEY: MultiSourceInput,
                                NAME_KEY: 'Wave Form',
                                'From a file': {
                                    ELEMENT_KEY: FileReader,
                                    'type': 'wav',
                                    'display_label': False,
                                },
                                'From the microphone': {
                                    ELEMENT_KEY: AudioRecorder,
                                    # "save_dir": rootdir,
                                },
                            },
                            'save_name': {NAME_KEY: 'Save as',},
                        },
                        'output': {
                            ELEMENT_KEY: SuccessNotification,
                            'message': 'The wave form has been uploaded successfully.',
                        },
                    }
                },
                'get_data': {
                    NAME_KEY: 'Data Explorer',
                    'execution': {
                        'output': {ELEMENT_KEY: AudioPlayer,},
                        'auto_submit': True,
                    },
                },
            },
        },
    )
    app()
