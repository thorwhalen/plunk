from typing import List, Dict, Union, TypedDict

from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
from front.elements import InputBase, OutputBase, ExecContainerBase
from plunk.ap.wf_visualize_player.wf_visualize_player_element import WfVisualizePlayer
from streamlitfront import mk_app
from streamlitfront.elements import SelectBox
from plunk.ap.session_table.session_table_element import OtoTable
import random
import pandas as pd
from dataclasses import dataclass
from st_aggrid import AgGrid
import pandas as pd
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import streamlit as st
from streamlitfront import binder as b
from plunk.sb.front_demo.user_story1.components.components import AudioArrayDisplay


class SessionQuery(TypedDict):
    filter: dict
    sort: dict
    pagination: dict


@dataclass
class Grid(InputBase):
    sessions: pd.DataFrame = None
    # on_value_change: callable = lambda x: print(x["selected_rows"])

    def render(self):
        gb = GridOptionsBuilder.from_dataframe(self.sessions)
        gb.configure_selection(selection_mode='multiple', use_checkbox=True)
        gridOptions = gb.build()

        data = AgGrid(
            self.sessions,
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            enable_enterprise_modules=True,
        )

        # print(dir(self))
        return data['selected_rows']


@dataclass
class MockGrid(InputBase):
    sessions: pd.DataFrame = None

    def render(self):
        st.write(self.sessions)


def retrieve_data(sref):
    import soundfile as sf
    import os

    # sref = "/Dropbox/OtoSense/VacuumEdgeImpulse/" + sref
    home_directory = os.path.expanduser('~')
    st.write(home_directory)
    path = os.path.join(home_directory + '/Dropbox/OtoSense/VacuumEdgeImpulse/', sref)

    # path = os.path.expanduser(sref)
    st.write(path)
    arr = sf.read(path, dtype='int16')[0]
    return path, arr


@dataclass
class WavSelectionViewer(OutputBase):
    def render(self):
        st.write('wav selection viewer')
        import soundfile as sf

        sref = self.output[0]['sref']
        path, arr = retrieve_data(sref)
        # arr = sf.read(sref, dtype="int16")[0]
        # st.write(type(arr))
        tab1, tab2 = st.tabs(['Audio Player', 'Waveform'])
        with tab1:
            # if not isinstance(sound, bytes):
            #     sound = sound.getvalue()
            # arr = sf.read(BytesIO(sound), dtype="int16")[0]
            st.write(f'type of data={type(sref)}')

            st.audio(path)
        with tab2:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(15, 5))
            ax.plot(arr)
            ax.legend()
            st.pyplot(fig)
            # st.write(arr[:10])


# @dataclass
# class WavSelectionViewer(AudioArrayDisplay):
#     def render(self):
#         print(f"output is rendered")
#         data = self.output
#         import soundfile as sf

#         data = sf.read(data[0]["sref"])
#         super().render(data)
#         st.write(self.output)


def random_sample_from_list(choices, k=1):
    return random.sample(choices, k=k)


DFLT_HEALTHY = ['Healthy_0', 'Healthy_1', 'Healthy_2']
DFLT_UNHEALTHY = ['Failure', 'Imbalance', 'Defect', 'Noise']


def random_int():
    return random.randint(0, 1)


def mock_annotations():
    choice = random_int()
    if choice == 0:
        return random_sample_from_list(
            DFLT_HEALTHY, k=random.randint(1, len(DFLT_HEALTHY))
        )
    else:
        return random_sample_from_list(
            DFLT_UNHEALTHY, k=random.randint(1, len(DFLT_HEALTHY))
        )


# adapted from Andie's code
def mock_session_gen(n: int = 10) -> List[Dict]:
    sessions = []
    time_step = 600000000
    sample_rates = [44100, 48000]

    for i in range(n):
        bt = 1677672000000000 + (i * time_step)
        tt = 1677672000000000 + ((i + 1) * time_step)

        sessions.append(
            {
                'ID': f'mockSession{i}',
                'device_id': f'deviceId{i % 2 + 1}',
                'bt': bt,
                'tt': tt,
                'sr': sample_rates[i % 2],
                #'bit_depth': 8,
                #'channels': channels,
                'annotations': mock_annotations(),
            }
        )

    return sessions


DFLT_FPATH = '../data/mock_data.csv'


def mk_dataset() -> pd.DataFrame:
    df = pd.read_csv(DFLT_FPATH)
    return df


MOCK_SESSIONS = mk_dataset()


def filterByNamesOperator(
    names: List[str], operator: str, namedList: List[Dict[str, str]]
) -> bool:
    if operator == 'and' and not all(
        name in [item['name'] for item in namedList] for name in names
    ):
        return False
    elif operator == 'or' and not any(
        name in [item['name'] for item in namedList] for name in names
    ):
        return False
    return True


def filterSessions(f: dict, sessions: List[dict]) -> List[dict]:
    _sessions = sessions.copy()
    return list(
        filter(
            lambda s: (
                (f.get('from_bt') is None or s['bt'] >= f['from_bt'])
                and (f.get('to_bt') is None or s['bt'] <= f['to_bt'])
                and (f.get('from_tt') is None or s['tt'] >= f['from_tt'])
                and (f.get('to_tt') is None or s['tt'] <= f['to_tt'])
                and (f.get('sr') is None or s['sr'] == f['sr'])
                and (
                    f.get('channels') is None
                    or filterByNamesOperator(
                        f['channels']['names'],
                        f['channels']['operator'],
                        [c['name'] for c in s['channels']],
                    )
                )
                and (
                    f.get('annotations') is None
                    or filterByNamesOperator(
                        f['annotations']['names'],
                        f['annotations']['operator'],
                        [a['name'] for a in s['annotations']],
                    )
                )
            ),
            _sessions,
        )
    )


def sort_sessions(sort, sessions: list):
    _sessions = sessions.copy()
    if len(_sessions) > 0:
        _field = sort['field']
        if sort['mode'] == 'asc':
            _sessions = sorted(_sessions, key=lambda s: s[_field])
        else:
            _sessions = sorted(_sessions, key=lambda s: s[_field], reverse=True)
    return _sessions


def mock_list_sessions(query: SessionQuery):
    s = MOCK_SESSIONS.copy()

    if not query:
        return s
    if _filter := query.get('filter'):
        s = filterSessions(_filter, s)

    if _sort := query.get('sort'):
        s = sort_sessions(_sort, s)

    if _pagination := query.get('pagination'):
        s = s[_pagination.get('from_idx') : _pagination.get('to_idx')]

    return s


def identity(x=None):
    st.write(b.selected_row())
    return x


def select_sessions(sessions):
    return sessions


def session_wf(sessions):
    if sessions:
        from plunk.ap.wf_visualize_player.wf_visualize_player_app import (
            wf_mix,
            wf_two_channel_sine_tone,
            wf_three_channel_mixed_sine_tone,
            wf_four_channel,
        )

        session = next(s for s in MOCK_SESSIONS if s.get('ID') == sessions[0])
        n_channels = len(session.get('channels', 1))
        example_wfs = {
            1: wf_mix,
            2: wf_two_channel_sine_tone,
            3: wf_three_channel_mixed_sine_tone,
            4: wf_four_channel,
        }

        return example_wfs[n_channels]()


# App
# features = [identity, session_wf]
def pre_configure_dpp(model_type, chk_size, featurizer):
    pass


features = [select_sessions, pre_configure_dpp]


config = {
    APP_KEY: {'title': 'DPP builder'},
    RENDERING_KEY: {
        'select_sessions': {
            NAME_KEY: 'Original dataset',
            'description': {
                'content': '''
                            Review carefully the dataset that will be used to train and test the model, then press NEXT.
                            If the dataset does not look right, close the DPP Builder, return to the Session List, 
                            and preselect the relevant sessions before reopening the DPP Builder.
                            '''
            },
            'execution': {
                'inputs': {
                    'sessions': {
                        ELEMENT_KEY: Grid,
                        'sessions': MOCK_SESSIONS,
                        # "value": b.selected_row,
                    },
                },
                'output': {ELEMENT_KEY: WavSelectionViewer},
                # "auto_submit": True,
            },
        },
        'pre_configure_dpp': {
            NAME_KEY: 'Pre-configure DPP',
            'description': {
                'content': '''
                            TBD
                            '''
            },
            'execution': {
                'inputs': {
                    'model_type': {
                        ELEMENT_KEY: SelectBox,
                        'options': ['Outlier model'],
                        'value': 'Outlier model',
                    },
                    'chk_size': {
                        ELEMENT_KEY: SelectBox,
                        'options': [1024, 512, 256],
                        'value': 1024,
                    },
                    'featurizer': {
                        ELEMENT_KEY: SelectBox,
                        'options': ['Default featurizer'],
                        # "value": 1024,
                    },
                },
                # "output": {ELEMENT_KEY: WavSelectionViewer},
                # "auto_submit": True,
            },
        },
    },
}


if __name__ == '__main__':
    app = mk_app(features, config=config)
    app()
