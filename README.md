# pytest-scim2-server

SCIM2 server fixture for Pytest

## Installation

```
pip install pytest-scim2-server
```

## Usage

pytest-scim2-server creates a ``scim2_server`` fixture that runs an instance of [scim2-server](https://scim2-server.readthedocs.io) on a random port, in a dedicated thread.
The server keeps the resources in memory, for the whole test session.

```python
import httpx2


def test_scim_foobar(scim2_server):
    res = httpx2.get(f"http://localhost:{scim2_server.port}/v2/Users")
    ...
```

Note that you can use [scim2-client](https://scim2-client.readthedocs.io) to interact with the SCIM server.

```python
import pytest
from httpx2 import Client
from scim2_client.engines.httpx2 import SyncSCIMClient


@pytest.fixture(scope="session")
def scim_client(scim2_server):
    http_client = Client(base_url=f"http://localhost:{scim2_server.port}/v2")
    scim_client = SyncSCIMClient(http_client)
    scim_client.discover()
    return scim_client


def test_scim2_server(scim_client):
    User = scim_client.get_resource_model("User")
    user = User(user_name="bjensen@example.com")
    response = scim_client.create(user)

    users = scim_client.query(User)
    assert users.resources[0].id == response.id
```

## Customize the server

The server is built from three fixtures. Override one of them in a `conftest.py` to change the server:

- `scim2_server_provider` returns the [`ScimProvider`](https://scim2-models.readthedocs.io/en/latest/reference/discovery.html#scim2_models.ScimProvider): the schemas, the resource types and the service provider configuration.
- `scim2_server_storage` returns the [storage](https://scim2-server.readthedocs.io/en/latest/how-to/write-a-storage.html) of the resources. It keeps them in memory by default.
- `scim2_server_service` returns the [`ScimService`](https://scim2-server.readthedocs.io/en/latest/reference/service.html#scim2_server.service.ScimService), built upon `scim2_server_provider`.

For instance, the following server does not support PATCH:

```python
import pytest
from scim2_server.utils import load_default_provider


@pytest.fixture(scope="session")
def scim2_server_provider():
    provider = load_default_provider()
    provider.config.patch.supported = False
    return provider
```

The fixtures are session-scoped, so an overriding fixture must be session-scoped too.

## Related projects

If you are working with SCIM and Python you might also want to have a look at:
- [scim2-server](https://scim2-server.readthedocs.io)
- [scim2-models](https://scim2-models.readthedocs.io)
- [scim2-client](https://scim2-client.readthedocs.io)
- [scim2-cli](https://scim2-cli.readthedocs.io)
- [scim2-tester](https://scim2-tester.readthedocs.io)
