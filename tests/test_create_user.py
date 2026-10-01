import pytest

from tests.api.schemas import assert_error, assert_user
from tests.api.user_factory import INVALID_FIELDS, build_user


def test_create_user_returns_201_and_persists_it(users_api, cleanup):
    user = build_user()

    response = users_api.create(user)
    cleanup.append(user["email"])

    assert response.status == 201
    assert_user(response)
    assert response.json() == user
    assert users_api.get(user["email"]).json() == user


@pytest.mark.parametrize("age", [1, 150], ids=["age-minimum", "age-maximum"])
def test_create_user_accepts_age_boundaries(users_api, cleanup, age):
    user = build_user(age=age)

    response = users_api.create(user)
    cleanup.append(user["email"])

    assert response.status == 201
    assert_user(response)
    assert response.json()["age"] == age


@pytest.mark.parametrize("invalid", INVALID_FIELDS)
def test_create_user_rejects_invalid_payload(users_api, cleanup, invalid):
    payload = build_user(**invalid)

    response = users_api.create(payload)
    if response.ok:
        cleanup.append(payload["email"])

    assert response.status == 400, f"Expected 400, got {response.status}: {response.text()}"
    assert_error(response)


def test_create_user_with_non_object_body_returns_400(users_api):
    response = users_api.create([])

    assert response.status == 400, f"Expected 400, got {response.status}: {response.text()}"
    assert_error(response)


def test_create_user_with_existing_email_returns_409(users_api, existing_user):
    duplicate = build_user(email=existing_user["email"], name="Someone Else")

    response = users_api.create(duplicate)

    assert response.status == 409, f"Expected 409, got {response.status}: {response.text()}"
    assert_error(response)
