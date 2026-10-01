import uuid

import pytest

MISSING = object()  # sentinel: drop the field from the payload


def build_user(**overrides) -> dict:
    """Valid user payload with a unique email. Override fields (or set them to MISSING) to break it."""
    user = {"name": "Jane Doe", "email": f"qa.{uuid.uuid4().hex[:10]}@example.com", "age": 30}
    user.update(overrides)
    return {field: value for field, value in user.items() if value is not MISSING}


# One case per validation rule the spec declares for Create/UpdateUserRequest:
# required fields, field types, age minimum/maximum and email format.
INVALID_FIELDS = [
    pytest.param({"name": MISSING}, id="missing-name"),
    pytest.param({"name": 123}, id="name-not-string"),
    pytest.param({"email": MISSING}, id="missing-email"),
    pytest.param({"age": MISSING}, id="missing-age"),
    pytest.param({"age": "thirty"}, id="age-not-integer"),
    pytest.param({"age": 0}, id="age-below-minimum"),
    pytest.param({"age": 151}, id="age-above-maximum"),
    pytest.param({"email": "not-an-email"}, id="email-bad-format"),
]
