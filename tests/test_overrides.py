def test_override_the_provider(pytester):
    """The application serves the configuration of an overridden provider."""
    pytester.makeconftest(
        """
        import pytest
        from scim2_server.utils import load_default_provider


        @pytest.fixture(scope="session")
        def scim2_server_provider():
            provider = load_default_provider()
            provider.config.patch.supported = False
            return provider
        """
    )
    pytester.makepyfile(
        """
        from httpx2 import Client
        from httpx2 import WSGITransport


        def test_config(scim2_server_app):
            client = Client(
                base_url="http://scim.test", transport=WSGITransport(app=scim2_server_app)
            )
            config = client.get("/v2/ServiceProviderConfig").json()
            assert config["patch"]["supported"] is False
        """
    )
    pytester.runpytest().assert_outcomes(passed=1)


def test_override_the_storage(pytester):
    """The application keeps the resources in an overridden storage."""
    pytester.makeconftest(
        """
        import pytest
        from scim2_server.memory import InMemoryStorage


        class RecordingStorage(InMemoryStorage):
            created = []

            def create(self, resource_type, resource):
                created = super().create(resource_type, resource)
                self.created.append(created.id)
                return created


        @pytest.fixture(scope="session")
        def scim2_server_storage():
            return RecordingStorage()
        """
    )
    pytester.makepyfile(
        """
        from httpx2 import Client
        from httpx2 import WSGITransport


        def test_create(scim2_server_app, scim2_server_storage):
            client = Client(
                base_url="http://scim.test", transport=WSGITransport(app=scim2_server_app)
            )
            response = client.post("/v2/Users", json={"userName": "bjensen"})
            assert scim2_server_storage.created == [response.json()["id"]]
        """
    )
    pytester.runpytest().assert_outcomes(passed=1)


def test_override_the_service(pytester):
    """The application serves the requests with an overridden service."""
    pytester.makeconftest(
        """
        import pytest
        from scim2_server.service import ScimService


        class PrefixedService(ScimService):
            def resource_location(self, base_url, resource_type, resource_id):
                return f"{base_url}/Accounts/{resource_id}"


        @pytest.fixture(scope="session")
        def scim2_server_service(scim2_server_provider):
            return PrefixedService(scim2_server_provider)
        """
    )
    pytester.makepyfile(
        """
        from httpx2 import Client
        from httpx2 import WSGITransport


        def test_location(scim2_server_app):
            client = Client(
                base_url="http://scim.test", transport=WSGITransport(app=scim2_server_app)
            )
            response = client.post("/v2/Users", json={"userName": "bjensen"})
            user_id = response.json()["id"]
            assert response.headers["Location"] == f"http://scim.test/v2/Accounts/{user_id}"
        """
    )
    pytester.runpytest().assert_outcomes(passed=1)


def test_the_application_uses_the_provider_of_the_service(pytester):
    """A service built upon another provider gives its provider to the application."""
    pytester.makeconftest(
        """
        import pytest
        from scim2_server.service import ScimService
        from scim2_server.utils import load_default_provider


        @pytest.fixture(scope="session")
        def scim2_server_service():
            return ScimService(load_default_provider())
        """
    )
    pytester.makepyfile(
        """
        def test_provider(scim2_server_app, scim2_server_service, scim2_server_provider):
            assert scim2_server_app.provider is scim2_server_service.provider
            assert scim2_server_app.provider is not scim2_server_provider
        """
    )
    pytester.runpytest().assert_outcomes(passed=1)


def test_request_logging(pytester):
    """The server logs the requests when the logging is enabled."""
    pytester.makepyfile(
        """
        from httpx2 import Client


        def test_log(scim2_server):
            scim2_server.logging = True
            Client().get(f"http://localhost:{scim2_server.port}/v2/Users")
        """
    )
    result = pytester.runpytest("-s")
    result.assert_outcomes(passed=1)
    assert "GET /v2/Users" in result.stderr.str()
