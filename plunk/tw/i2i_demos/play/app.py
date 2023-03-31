from extrude import mk_web_app

from resources import funcs
from configurations import config

if __name__ == '__main__':

    app = mk_web_app(funcs, config=config, api_url='http://localhost:3030/openapi')
    app()
