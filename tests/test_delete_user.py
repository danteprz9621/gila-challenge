import pytest

from tests.api.schemas import assert_error, assert_no_content
from tests.api.settings import VALID_TOKEN
from tests.api.user_factory import build_user


def test_delete_user_returns_204_and_removes_it(users_api, existing_user):
    response = users_api.delete(existing_user["email"], token=VALID_TOKEN)

    assert_no_content(response)
    assert existing_user not in users_api.list_all().json()


@pytest.mark.parametrize("token", [None, "wrong-token"], ids=["missing-token", "invalid-token"])
def test_delete_user_without_valid_token_returns_401(users_api, existing_user, token):
    response = users_api.delete(existing_user["email"], token=token)

    assert response.status == 401, f"Expected 401, got {response.status}: {response.text()}"
    assert_error(response)
    assert existing_user in users_api.list_all().json(), "User was deleted without valid authentication"


def test_delete_unknown_user_returns_404(users_api):
    response = users_api.delete(build_user()["email"], token=VALID_TOKEN)

    assert response.status == 404, f"Expected 404, got {response.status}: {response.text()}"
    assert_error(response)
