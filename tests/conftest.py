import pytest
from playwright.sync_api import sync_playwright

from tests.api.settings import API_URL, ENVIRONMENTS, TARGET_ENV, VALID_TOKEN
from tests.api.user_factory import build_user
from tests.api.users_client import UsersClient


def pytest_addoption(parser):
    parser.addoption("--env", default=TARGET_ENV, choices=ENVIRONMENTS, help="Environment under test")
    parser.addoption("--api-url", default=API_URL, help="Host serving the User Management API")


def pytest_report_header(config):
    return f"API: {config.getoption('--api-url')}  |  environment: {config.getoption('--env')}"


@pytest.fixture(scope="session")
def env(pytestconfig) -> str:
    return pytestconfig.getoption("--env")


@pytest.fixture(scope="session")
def request_context(pytestconfig):
    with sync_playwright() as p:
        context = p.request.new_context(base_url=pytestconfig.getoption("--api-url"))
        yield context
        context.dispose()


@pytest.fixture(scope="session")
def users_api(request_context, env) -> UsersClient:
    return UsersClient(request_context, env)


@pytest.fixture(scope="session")
def other_env_api(request_context, env) -> UsersClient:
    other = next(e for e in ENVIRONMENTS if e != env)
    return UsersClient(request_context, other)


@pytest.fixture
def cleanup(users_api):
    """Collects emails created during a test and deletes them afterwards."""
    emails = []
    yield emails
    for email in emails:
        users_api.delete(email, token=VALID_TOKEN)


@pytest.fixture
def existing_user(users_api, cleanup) -> dict:
    user = build_user()
    response = users_api.create(user)
    assert response.status == 201, f"Setup failed creating user: {response.status} {response.text()}"
    cleanup.append(user["email"])
    return user
