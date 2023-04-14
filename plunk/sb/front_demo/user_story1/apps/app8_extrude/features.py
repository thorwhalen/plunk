import time
from functools import partial
from typing import List, Optional
import soundfile as sf
from front.crude import prepare_for_crude_dispatch
from olab import (
    WaveForm,
    scores_to_intervals,
    mk_step as olab_mk_step,
    # modify_step as olab_modify_step,
    mk_pipeline as olab_mk_pipeline,
    # modify_pipeline as olab_modify_pipeline,
    learn_outlier_model as olab_learn_outlier_model,
    apply_fitted_model as olab_apply_fitted_model,
)
from recode import decode_wav_header_bytes
from streamlit.runtime.uploaded_file_manager import UploadedFile

from platform_poc.data import mall

crudifier = partial(
    prepare_for_crude_dispatch, mall=mall, include_stores_attribute=True
)


# def value_list_getter(store_name: str):
#     def get_value_list(mall, keys):
#         return [v for k, v in mall[store_name].items() if k in keys]

#     return get_value_list


@crudifier(output_store='tagged_data', output_trans=lambda: None)
def upload_audio_data(audio_data: List[WaveForm], tag: str):
    return audio_data, tag


# @crudifier(param_to_mall_map=dict(step_factory='step_factories'), output_store='steps', output_trans=lambda: None)
# def mk_step(step_factory: Literal['chunker', 'featurizer'], kwargs: dict, save_name: str):
#     sf = mall['step_factories'][step_factory]
#     mall['steps'][save_name] = olab_mk_step(sf, kwargs)


mk_step = crudifier(
    olab_mk_step,
    param_to_mall_map=dict(step_factory='step_factories'),
    output_store='steps',
    output_trans=lambda: None,
)

# modify_step = crudifier(
#     olab_modify_step,
#     param_to_mall_map=dict(step_to_modify="steps"),
#     output_store="steps",
#     output_trans=lambda: None,
# )

mk_pipeline = crudifier(
    olab_mk_pipeline,
    param_to_mall_map=['steps'],
    output_store='pipelines',
    output_trans=lambda: None,
)

# modify_pipeline = crudifier(
#     olab_modify_pipeline,
#     param_to_mall_map=dict(pipeline="pipelines"),
#     output_store="pipelines",
#     output_trans=lambda: None,
# )

learn_outlier_model = crudifier(
    olab_learn_outlier_model,
    param_to_mall_map=dict(tagged_data='tagged_data', preprocess_pipeline='pipelines'),
    output_store='learned_models',
    output_trans=lambda: None,
)
apply_fitted_model = crudifier(
    olab_apply_fitted_model,
    param_to_mall_map=dict(
        tagged_data='tagged_data',
        preprocess_pipeline='pipelines',
        fitted_model='learned_models',
    ),
    output_store='model_outputs',
)


# @crudifier(param_to_mall_map=dict(pipeline='pipelines'),)
# def visualize_pipeline(pipeline: Pipeline):
#     return pipeline.pipe


@crudifier(param_to_mall_map=dict(model_output='model_outputs'),)
def visualize_output(model_output, threshold=80, num_segs=3):
    intervals = scores_to_intervals(model_output, threshold, num_segs)

    return model_output, intervals


# from front.crude import Crudifier, crudify_based_on_names
# from front.util import deep_merge
# from operator import attrgetter
# from front import RENDERING_KEY, ELEMENT_KEY, NAME_KEY
# from i2 import name_of_obj
# from itertools import chain
# from typing import TypeVar, Tuple, Iterable, Callable
# from streamlitfront.elements import (
#     SuccessNotification,
#     FileUploader,
# )


# general_crudifier = partial(
#     crudify_based_on_names,
#     param_to_mall_map={
#         "step_factory": "step_factories",
#         "tagged_data": "tagged_data",
#         "preprocess_pipeline": "pipelines",
#         "fitted_model": "learned_models",
#         "pipeline": "pipelines",
#         "scores": "model_outputs",
#     },
#     output_store={
#         upload_audio_data: "tagged_data",
#         mk_step: "steps",
#         mk_pipeline: "pipelines",
#         learn_outlier_model: "learned_models",
#         apply_fitted_model: "model_outputs",
#         visualize_pipeline: "pipelines",
#     },
#     crudifier=partial(prepare_for_crude_dispatch, mall=mall),
# )


# def crudify_all(funcs, crudifier=general_crudifier):
#     return map(crudifier, funcs)


# all_funcs = [
#     upload_audio_data,
#     mk_step,
#     mk_pipeline,
#     learn_outlier_model,
#     apply_fitted_model,
#     visualize_pipeline,
#     visualize_output,
# ]

# [
#     upload_audio_data,
#     mk_step,
#     mk_pipeline,
#     learn_outlier_model,
#     apply_fitted_model,
#     visualize_pipeline,
#     visualize_output,
# ] = list(crudify_all(all_funcs))


# def has_metadata(obj: Obj, data="front_spec") -> bool:
#     return hasattr(obj, data)


# DFLT_COND = partial(has_metadata, data="front_spec")
# DFLT_RETRIEVE_SPEC = attrgetter("front_spec")


# def config_from_attribute(obj: Obj, retrieve_spec: Callable = DFLT_RETRIEVE_SPEC):
#     spec_for_obj = retrieve_spec(obj)
#     obj_config = {
#         RENDERING_KEY: {name_of_obj(obj): spec_for_obj},
#     }

#     return obj_config


# # taken from:
# # https://github.com/otosense/plunk/blob/master/plunk/vf/front/custom_app_maker.py
# Obj = TypeVar("Obj")
# Output = TypeVar("Output")
# Cond = Callable[[Obj], bool]
# Then = Callable[[Obj], Output]
# Rule = Tuple[Cond, Then]
# Rules = Iterable[Rule]


# def mk_find_render_keys(obj: Obj, rules: Rules) -> Iterable[Output]:
#     for cond, then in rules:
#         if cond(obj):
#             yield then(obj)


# def deep_merge_list(obj, updates):
#     for update in updates:
#         obj = deep_merge(obj, update)
#     return obj


# def gather_configs(objs, rules, config=None):
#     config = config or {}
#     config_updates = chain.from_iterable(
#         mk_find_render_keys(obj, rules) for obj in objs
#     )
#     config_updates = list(config_updates)
#     config = deep_merge_list(config, config_updates)

#     return config


# def attribute_wrapper(attr_name, attr_value):
#     """attach an attribute to a function"""

#     def wrapper(func):
#         setattr(func, attr_name, attr_value)
#         return func

#     return wrapper


# upload_audio_data = attribute_wrapper(
#     "front_spec",
#     {
#         "execution": {
#             "inputs": {
#                 "audio_data": {
#                     ELEMENT_KEY: FileUploader,
#                     "type": "wav",
#                     "accept_multiple_files": True,
#                 },
#             },
#             "output": {
#                 ELEMENT_KEY: SuccessNotification,
#                 "message": "Wav files loaded successfully.",
#             },
#         },
#     },
# )(upload_audio_data)


def visualize_session(session: Optional[str]):
    # Get wav file for session
    if session is None:
        return

    _, group, upload_id, *_ = session.split('_')
    upload_id = int(upload_id)
    files, _ = mall['tagged_data'][group]
    for f in files:
        if f.id == upload_id:
            return sf.read(f)


def mk_uploaded_file_session(uploaded_file: UploadedFile, tag, bt, group) -> dict:
    wav_bytes = uploaded_file.getvalue()
    wav_header = decode_wav_header_bytes(wav_bytes)
    sr = wav_header['sr']
    bit_depth = wav_header['width_bytes'] * 8
    n_ch = wav_header['n_channels']
    n_frames = wav_header['nframes']

    channels = [
        {'name': f'ch{ch_idx}', 'description': uploaded_file.name}
        for ch_idx in range(n_ch)
    ]
    tt = bt + n_frames / sr * 1e6

    return {
        'ID': f'mockSession_{group}_{uploaded_file.id}_{uploaded_file.name}',
        'device_id': f'mockDeviceId',
        'bt': bt,
        'tt': tt,
        'sr': sr,
        'bit_depth': bit_depth,
        'channels': channels,
        'annotations': [{'name': tag, 'bt': bt, 'tt': tt}],
    }


def list_sessions(*_a, **_kw) -> List[dict]:
    """Fetch mock sessions based on tagged data"""
    sessions = []
    bt = time.time() * 1e6
    for group, (files, tag) in mall['tagged_data'].items():
        for f in files:
            s = mk_uploaded_file_session(f, tag, bt, group)
            sessions.append(s)
            bt = s['tt']
    return sessions
