from typing import List, Dict, Union

from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
from streamlitfront import mk_app, binder as b

from plunk.ap.session_table.session_table_element import (
    SessionQuery,
    OtoTableAll,
)


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


if __name__ == '__main__':

    def identity(x):
        return x

    app = mk_app(
        [identity],
        config={
            APP_KEY: {'title': 'Session Table'},
            RENDERING_KEY: {
                # 'list_session': {
                #     NAME_KEY: 'Session Table',
                #     'description': {'content': 'Session Table'},
                #     'execution': {
                #         'inputs': {'query': {ELEMENT_KEY: OtoTableQuery,},},
                #         'output': {ELEMENT_KEY: OtoTable},
                #         'auto_submit': True,
                #     },
                # },
                'identity': {
                    NAME_KEY: 'Session Table',
                    'description': {'content': 'Session Table'},
                    'execution': {
                        'inputs': {
                            'x': {
                                ELEMENT_KEY: OtoTableAll,
                                'list_session': mock_list_sessions,
                                'query': b.oto_table_query,
                            },
                        },
                        # 'output': {ELEMENT_KEY: Pass},
                        'auto_submit': True,
                    },
                },
            },
        },
    )
    app()
