from streamlitfront.elements import SessionTable

from typing import List, Dict, Union

# Session = Dict[str, Union[str, int, List[Dict[str, Union[str, int]]]]]


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
                'annotations': mock_annotations(bt, tt, time_step / 10, i % 5 + 1),
            }
        )

    return sessions


#
#
# from typing import List, Optional, Dict
#
#
# class Annotation:
#     def __init__(self, name: str, bt: int, tt: int):
#         self.name = name
#         self.bt = bt
#         self.tt = tt
#
#
# class Channel:
#     def __init__(self, name: str, description: str):
#         self.name = name
#         self.description = description
#
#
# class Session:
#     def __init__(
#         self,
#         ID: str,
#         device_id: str,
#         bt: int,
#         tt: int,
#         sr: int,
#         bit_depth: int,
#         channels: List[Channel],
#         annotations: List[Annotation],
#     ):
#         self.ID = ID
#         self.device_id = device_id
#         self.bt = bt
#         self.tt = tt
#         self.sr = sr
#         self.bit_depth = bit_depth
#         self.channels = channels
#         self.annotations = annotations
#
#
# def mockAnnotations(start: int, stop: int, step: int, tag: int) -> List[Annotation]:
#     annotations = []
#     t = 1
#     for i in range(start, stop, step):
#         annotations.append(Annotation(f'tag{t}', i, i + step))
#         t = (t % tag) + 1
#     return annotations
#
#
# def mockSessionGen(n: int = 10) -> List[Session]:
#     sessions = []
#     timeStep = 600000000
#     sampleRates = [44100, 48000]
#     for i in range(n):
#         bt = 1677672000000000 + (i * timeStep)
#         tt = 1677672000000000 + ((i + 1) * timeStep)
#         channels = []
#         for j in range(i % 4 + 1):
#             channels.append(Channel(f'ch{j}', 'microphone'))
#         sessions.append(
#             Session(
#                 f'mockSession{i}',
#                 f'deviceId{(i % 2) + 1}',
#                 bt,
#                 tt,
#                 sampleRates[i % 2],
#                 8,
#                 channels,
#                 mockAnnotations(bt, tt, timeStep // 10, (i % 5) + 1),
#             )
#         )
#     return sessions
#
#
# def filterByNamesOperator(
#     names: List[str], operator: str, namedList: List[Dict[str, str]]
# ) -> bool:
#     if operator == 'and' and not all(
#         name in [item['name'] for item in namedList] for name in names
#     ):
#         return False
#     elif operator == 'or' and not any(
#         name in [item['name'] for item in namedList] for name in names
#     ):
#         return False
#     return True
#
#
# def filterSessions(
#     f: Dict[str, Optional[int]], sessions: List[Session] = mockSessionGen(100)
# ) -> List[Session]:
#     _sessions = sessions[:]
#     return list(
#         filter(
#             lambda s: (
#                 (f['from_bt'] is None or s.bt >= f['from_bt'])
#                 and (f['to_bt'] is None or s.bt <= f['to_bt'])
#                 and (f['from_tt'] is None or s.tt >= f['from_tt'])
#                 and (f['to_tt'] is None or s.tt <= f['to_tt'])
#                 and (f['sr'] is None or s.sr == f['sr'])
#                 and (
#                     f['channels'] is None
#                     or filterByNamesOperator(
#                         f['channels']['names'],
#                         f['channels']['operator'],
#                         [vars(c) for c in s.channels],
#                     )
#                 )
#                 and (
#                     f['annotations'] is None
#                     or filterByNamesOperator(
#                         f['annotations']['names'],
#                         f['annotations']['operator'],
#                         [vars(a) for a in s.annotations],
#                     )
#                 )
#             ),
#             _sessions,
#         )
#     )


def list_session(*a, **kw):
    return mock_session_gen(100)


def get_list_session_api():
    return list_session


if __name__ == '__main__':
    from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
    from streamlitfront import mk_app

    app = mk_app(
        [get_list_session_api],
        config={
            APP_KEY: {'title': 'Session Table'},
            RENDERING_KEY: {
                'get_list_session_api': {
                    NAME_KEY: 'Session Table',
                    'description': {'content': 'Session Table'},
                    'execution': {
                        'output': {ELEMENT_KEY: SessionTable},
                        'auto_submit': True,
                    },
                },
            },
        },
    )
    app()
