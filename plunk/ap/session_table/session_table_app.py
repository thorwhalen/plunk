from typing import List, Dict, Union, TypedDict

from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
from plunk.ap.wf_visualize_player.wf_visualize_player_element import WfVisualizePlayer
from streamlitfront import mk_app

from plunk.ap.session_table.session_table_element import OtoTable


class SessionQuery(TypedDict):
    filter: dict
    sort: dict
    pagination: dict


def mock_annotations(
    start: int, stop: int, step: int, tag: int
) -> List[Dict[str, Union[str, int]]]:
    annotations = []
    t = 1

    for i in range(start, stop, step):
        annotations.append({'name': f'tag{t}', 'bt': i, 'tt': i + step})

        t = t % tag + 1

    return annotations


def mock_session_gen(n: int = 10) -> List[Dict]:
    sessions = []
    time_step = 600000000
    sample_rates = [44100, 48000]

    for i in range(n):
        bt = 1677672000000000 + (i * time_step)
        tt = 1677672000000000 + ((i + 1) * time_step)
        channels = []

        for j in range(i % 4 + 1):
            channels.append({'name': f'ch{j}', 'description': 'microphone'})

        sessions.append(
            {
                'ID': f'mockSession{i}',
                'device_id': f'deviceId{i % 2 + 1}',
                'bt': bt,
                'tt': tt,
                'sr': sample_rates[i % 2],
                'bit_depth': 8,
                'channels': channels,
                'annotations': mock_annotations(bt, tt, int(time_step / 10), i % 5 + 1),
            }
        )

    return sessions


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


MOCK_SESSIONS = mock_session_gen(1000)


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


def identity(x):
    return x


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


features = [identity, session_wf]

config = {
    APP_KEY: {'title': 'Session Table'},
    RENDERING_KEY: {
        'identity': {
            NAME_KEY: 'Session Table Multiselect',
            'description': {'content': 'Session Table Multiselect'},
            'execution': {
                'inputs': {
                    'x': {
                        ELEMENT_KEY: OtoTable,
                        'sessions': MOCK_SESSIONS,
                        'is_multiselect': True,
                    },
                },
                'auto_submit': True,
            },
        },
        'session_wf': {
            NAME_KEY: 'Session Table Single Select',
            'description': {'content': 'Session Table Single Select'},
            'execution': {
                'inputs': {
                    'sessions': {
                        ELEMENT_KEY: OtoTable,
                        'sessions': MOCK_SESSIONS,
                        'is_multiselect': False,
                    },
                },
                'output': {ELEMENT_KEY: WfVisualizePlayer},
                'auto_submit': True,
            },
        },
    },
}


if __name__ == '__main__':
    app = mk_app(features, config=config)
    app()
