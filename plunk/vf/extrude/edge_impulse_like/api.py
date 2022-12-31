import os
from extrude import mk_api, run_api
from py2http.decorators import handle_binary_req, send_binary_resp
from i2 import Sig

from plunk.vf.extrude.edge_impulse_like import upload_data, get_data, mall


@handle_binary_req
@Sig(upload_data)
def upload_data_input_handler(**kwargs):
    return kwargs


@send_binary_resp
def get_data_output_handler(output, **input_kwargs):
    return output


handlers = [
    dict(endpoint=upload_data, input_mapper=upload_data_input_handler,),
    dict(endpoint=get_data, output_mapper=get_data_output_handler,)
    # get_data
]
_app = mk_api(handlers, mall)
api_url = _app.openapi_spec['servers'][0]['url']


if __name__ == '__main__':
    run_api(_app)
