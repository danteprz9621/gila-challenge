"""Response contracts loaded straight from the OpenAPI spec, so the spec stays the single source of truth."""
from pathlib import Path

import yaml
from jsonschema import validate
from playwright.sync_api import APIResponse

SPEC_PATH = Path(__file__).resolve().parents[2] / "spec" / "sdet_challenge_api.yml"
_SCHEMAS = yaml.safe_load(SPEC_PATH.read_text())["components"]["schemas"]


def _json_body(response: APIResponse):
    content_type = response.headers.get("content-type", "")
    assert content_type.startswith("application/json"), f"Expected JSON response, got '{content_type}'"
    return response.json()


def assert_user(response: APIResponse) -> None:
    validate(instance=_json_body(response), schema=_SCHEMAS["User"])


def assert_user_list(response: APIResponse) -> None:
    validate(instance=_json_body(response), schema={"type": "array", "items": _SCHEMAS["User"]})


def assert_error(response: APIResponse) -> None:
    validate(instance=_json_body(response), schema=_SCHEMAS["ErrorResponse"])


def assert_no_content(response: APIResponse) -> None:
    assert response.status == 204
    assert response.body() == b"", f"204 must have an empty body, got: {response.text()}"
