from urllib.parse import urljoin
from extrude import mk_web_app
from http2py import HttpClient

from plunk.ap.session_table.extrude_web_service import API_URL
from plunk.ap.session_table.session_table_app import features, config


def main():
    api = HttpClient(url=urljoin(API_URL, 'openapi'))
    app = mk_web_app(features, api=api, config=config,)
    app()


if __name__ == '__main__':
    main()
