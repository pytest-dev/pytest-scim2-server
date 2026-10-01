import threading
from collections.abc import Iterator
from dataclasses import dataclass
from wsgiref.simple_server import WSGIRequestHandler
from wsgiref.simple_server import make_server

import portpicker
import pytest
from scim2_server.backend import InMemoryBackend
from scim2_server.provider import SCIMApplication
from scim2_server.utils import load_default_provider


@dataclass
class Server:
    """A proxy object that is returned by the pytest fixture."""

    port: int
    """The port on which the local http server listens."""

    app: SCIMApplication
    """The scim2-server WSGI application."""

    logging: bool = False
    """Whether the request access log is enabled."""

    def make_request_handler(self) -> type[WSGIRequestHandler]:
        server = self

        class RequestHandler(WSGIRequestHandler):
            def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
                if server.logging:
                    super().log_request(code, size)

        return RequestHandler


@pytest.fixture(scope="session")
def scim2_server_app() -> SCIMApplication:
    """SCIM2 server WSGI application."""
    return SCIMApplication(InMemoryBackend(), load_default_provider())


@pytest.fixture(scope="session")
def scim2_server_object(scim2_server_app: SCIMApplication) -> Server:
    """SCIM2 server object."""
    port = portpicker.pick_unused_port()
    return Server(port=port, app=scim2_server_app)


@pytest.fixture(scope="session")
def scim2_server(scim2_server_object: Server) -> Iterator[Server]:
    """SCIM2 server running in a thread."""
    host = "localhost"

    httpd = make_server(
        host,
        scim2_server_object.port,
        scim2_server_object.app,
        handler_class=scim2_server_object.make_request_handler(),
    )

    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()

    try:
        yield scim2_server_object
    finally:
        httpd.shutdown()
        server_thread.join()
