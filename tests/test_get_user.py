from tests.api.schemas import assert_error, assert_user
from tests.api.user_factory import build_user


def test_get_user_returns_200_with_user(users_api, existing_user):
    response = users_api.get(existing_user["email"])

    assert response.status == 200
    assert_user(response)
    assert response.json() == existing_user


def test_get_unknown_user_returns_404(users_api):
    response = users_api.get(build_user()["email"])

    assert response.status == 404, f"Expected 404, got {response.status}: {response.text()}"
    assert_error(response)
