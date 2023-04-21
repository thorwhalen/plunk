from py2http.decorators import (
    handle_binary_req,
    send_binary_resp,
    send_json_resp,
    handle_json_req,
)
from i2 import Sig

from platform_poc.apps.web_service.util_endpoints import (
    get_pipeline,
    get_step_factory_sig,
)
from platform_poc.features import (
    upload_audio_data,
    mk_step,
    # modify_step,
    mk_pipeline,
    # modify_pipeline,
    learn_outlier_model,
    apply_fitted_model,
    visualize_output,
    visualize_session,
    list_sessions,
)


@handle_binary_req
@Sig(upload_audio_data)
def upload_audio_data_input_handler(**kwargs):
    return kwargs


@send_binary_resp
def send_binary_resp_output_handler(output, **input_kwargs):
    return output


@send_json_resp
def send_json_resp_output_handler(output, **input_kwargs):
    return output


handlers = [
    # feature endpoints
    dict(endpoint=upload_audio_data, input_mapper=upload_audio_data_input_handler,),
    mk_step,
    # modify_step,
    mk_pipeline,
    # modify_pipeline,
    learn_outlier_model,
    dict(endpoint=apply_fitted_model, output_mapper=send_binary_resp_output_handler,),
    dict(endpoint=visualize_output, output_mapper=send_binary_resp_output_handler,),
    dict(endpoint=list_sessions, output_mapper=send_json_resp_output_handler,),
    dict(endpoint=visualize_session, output_mapper=send_binary_resp_output_handler,),
    # util endpoints
    dict(endpoint=get_step_factory_sig, output_mapper=send_binary_resp_output_handler,),
    dict(endpoint=get_pipeline, output_mapper=send_binary_resp_output_handler,),
]
