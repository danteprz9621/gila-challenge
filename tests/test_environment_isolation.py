def test_user_created_in_one_environment_is_not_visible_in_the_other(users_api, other_env_api, existing_user):
    assert existing_user in users_api.list_all().json()
    assert existing_user not in other_env_api.list_all().json(), (
        f"User created in /{users_api.env} leaked into /{other_env_api.env}"
    )
