import os
from extrude import mk_api, run_api

from plunk.sb.front_demo.user_story1.apps.app8_extrude.data.mall import mall
from plunk.sb.front_demo.user_story1.apps.app8_extrude.apps.web_service.handlers import (
    handlers,
)

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 3030))
API_URL = os.environ.get("API_URL", f"http://localhost:{PORT}")
SERVER = os.environ.get("SERVER", "wsgiref")
# SERVER = os.environ.get("SERVER", "gunicorn")


def main():
    print(f"Server: {SERVER}")
    app = mk_api(handlers, mall, api_url="http://localhost:3030/openapi")
    run_api(app, host=HOST, port=PORT, server=SERVER)


if __name__ == "__main__":
    print(f"Server: {SERVER}")
    main()
