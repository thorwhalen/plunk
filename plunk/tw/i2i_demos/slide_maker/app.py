from extrude import mk_web_app
from streamlitfront.tools import validate_config
from resources import funcs

import importlib
import configurations

importlib.reload(configurations)

from configurations import config

if __name__ == '__main__':
    validate_config(config, funcs)  # validate config against funcs
    app = mk_web_app(funcs, config=config, api_url='http://localhost:3030/openapi')
    app()
