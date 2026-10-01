from tests.api.schemas import assert_user_list


def test_list_users_returns_array_containing_created_user(users_api, existing_user):
    response = users_api.list_all()

    assert response.status == 200
    assert_user_list(response)
    assert existing_user in response.json()
