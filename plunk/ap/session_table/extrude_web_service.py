import os
from extrude import mk_api, run_api
from py2http.decorators import send_binary_resp

from plunk.ap.session_table.session_table_app import identity, session_wf

WS_PORT = int(os.environ.get('WS_PORT', 3030))
API_URL = os.environ.get('API_URL', f'http://localhost:{WS_PORT}')
SERVER = os.environ.get('SERVER', 'gunicorn')


@send_binary_resp
def send_binary_resp_output_handler(output, **input_kwargs):
    return output


handlers = [
    identity,
    {'endpoint': session_wf, 'output_mapper': send_binary_resp_output_handler},
]


def main(server=SERVER):
    app = mk_api(
        funcs=handlers,
        mall=None,
        host='0.0.0.0',
        port=WS_PORT,
        openapi=dict(base_url=API_URL),
        server=server,
    )
    run_api(app)


if __name__ == '__main__':
    main()
