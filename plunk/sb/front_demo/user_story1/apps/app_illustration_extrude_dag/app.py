from urllib.parse import urljoin
from extrude import mk_web_app
from http2py import HttpClient


from platform_poc.apps.web_service import API_URL
from configurations import mk_config
from resources import funcs


def main():
    features = funcs
    api = HttpClient(url=urljoin(API_URL, "openapi"))
    app = mk_web_app(
        features,
        api=api,
        config=mk_config(api),
    )
    app()


if __name__ == "__main__":
    main()
