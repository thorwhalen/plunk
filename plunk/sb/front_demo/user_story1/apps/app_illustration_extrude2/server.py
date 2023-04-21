import os
from extrude import mk_api, run_api
from mall import mall

from resources import funcs


HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 3030))
API_URL = os.environ.get("API_URL", f"http://localhost:{PORT}")
SERVER = os.environ.get("SERVER", "wsgiref")


handlers = funcs


def main():
    app = mk_api(handlers, mall, openapi=dict(base_url=API_URL))
    run_api(app, host=HOST, port=PORT, server=SERVER)


if __name__ == "__main__":
    main()
