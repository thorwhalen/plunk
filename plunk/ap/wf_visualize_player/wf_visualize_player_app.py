from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
from streamlitfront import mk_app

from plunk.ap.wf_visualize_player.test_data import (
    wf_sine,
    wf_bleeps,
    wf_mix,
    wf_pure_tone,
)
from plunk.ap.wf_visualize_player.wf_visualize_player_element import WfVisualizePlayer

if __name__ == '__main__':
    app = mk_app(
        [wf_sine, wf_bleeps, wf_mix, wf_pure_tone],
        config={
            APP_KEY: {'title': 'Waveform Visualization Player'},
            RENDERING_KEY: {
                'wf_sine': {
                    NAME_KEY: 'Sine',
                    'description': {'content': 'Sine Waveform'},
                    'execution': {'output': {ELEMENT_KEY: WfVisualizePlayer},},
                },
                'wf_bleeps': {
                    NAME_KEY: 'Bleeps',
                    'description': {'content': 'Bleeps Waveform'},
                    'execution': {'output': {ELEMENT_KEY: WfVisualizePlayer},},
                },
                'wf_mix': {
                    NAME_KEY: 'Mixed',
                    'description': {'content': 'Mixed Frequency Waveform'},
                    'execution': {'output': {ELEMENT_KEY: WfVisualizePlayer},},
                },
                'wf_pure_tone': {
                    NAME_KEY: 'Pure Tone',
                    'description': {'content': 'Pure Tone Waveform'},
                    'execution': {'output': {ELEMENT_KEY: WfVisualizePlayer},},
                },
            },
        },
    )
    app()
