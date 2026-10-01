import pytest

from tests.api.schemas import assert_error, assert_user
from tests.api.user_factory import INVALID_FIELDS, build_user


def test_update_user_returns_200_and_persists_changes(users_api, existing_user):
    changes = build_user(email=existing_user["email"], name="Jane Updated", age=31)

    response = users_api.update(existing_user["email"], changes)

    assert response.status == 200
    assert_user(response)
    assert response.json() == changes
    assert users_api.get(existing_user["email"]).json() == changes


@pytest.mark.parametrize("invalid", INVALID_FIELDS)
def test_update_user_rejects_invalid_payload(users_api, existing_user, invalid):
    payload = build_user(**{"email": existing_user["email"], **invalid})

    response = users_api.update(existing_user["email"], payload)

    assert response.status == 400, f"Expected 400, got {response.status}: {response.text()}"
    assert_error(response)


def test_update_unknown_user_returns_404(users_api):
    user = build_user()

    response = users_api.update(user["email"], user)

    assert response.status == 404, f"Expected 404, got {response.status}: {response.text()}"
    assert_error(response)


def test_update_user_to_existing_email_returns_409(users_api, existing_user, cleanup):
    other = build_user()
    assert users_api.create(other).status == 201
    cleanup.append(other["email"])

    response = users_api.update(existing_user["email"], {**existing_user, "email": other["email"]})

    assert response.status == 409, f"Expected 409, got {response.status}: {response.text()}"
    assert_error(response)
