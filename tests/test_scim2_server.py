import pytest
from httpx import Client
from scim2_client.engines.httpx import SyncSCIMClient


@pytest.fixture(scope="session")
def scim_client(scim2_server):
    http_client = Client(base_url=f"http://localhost:{scim2_server.port}")
    scim_client = SyncSCIMClient(http_client)
    scim_client.discover()
    return scim_client


def test_scim2_server(scim_client):
    User = scim_client.get_resource_model("User")
    user = User(user_name="bjensen@example.com")
    response = scim_client.create(user)

    users = scim_client.query(User)
    assert users.resources[0].id == response.id
