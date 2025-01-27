import threading
import wsgiref.simple_server
from dataclasses import dataclass

import portpicker
import pytest
from scim2_server.backend import InMemoryBackend
from scim2_server.provider import SCIMProvider
from scim2_server.utils import load_default_resource_types
from scim2_server.utils import load_default_schemas


@dataclass
class Server:
    """A proxy object that is returned by the pytest fixture."""

    port: int
    """The port on which the local http server listens."""

    app: SCIMProvider
    """The scim2-server WSGI application."""


@pytest.fixture(scope="session")
def scim2_server():
    """SCIM2 server running in a thread."""
    backend = InMemoryBackend()
    provider = SCIMProvider(backend)

    for schema in load_default_schemas().values():
        provider.register_schema(schema)

    for resource_type in load_default_resource_types().values():
        provider.register_resource_type(resource_type)

    host = "localhost"
    port = portpicker.pick_unused_port()
    httpd = wsgiref.simple_server.make_server(host, port, provider)

    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()

    server = Server(port=port, app=provider)

    try:
        yield server
    finally:
        httpd.shutdown()
        server_thread.join()
