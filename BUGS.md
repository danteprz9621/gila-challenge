# Bug Report — User Management API v1.0

Discrepancies between the running application (`ghcr.io/danielsilva-loanpro/sdet-interview-challenge:latest`)
and the contract in [`spec/sdet_challenge_api.yml`](spec/sdet_challenge_api.yml).

The spec states that `/dev` and `/prod` have **identical behavior**, so every bug was checked in both.

## Summary

| ID | Endpoint | Expected | Actual | dev | prod | Severity |
|----|----------|----------|--------|:---:|:----:|----------|
| [BUG-001](#bug-001) | `DELETE /users/{email}` | 401 without a valid token | 204, user deleted | ❌ | ✅ | Critical |
| [BUG-002](#bug-002) | `PUT /users/{email}` | Changes persisted | 200 but changes are lost | ❌ | ❌ | High |
| [BUG-003](#bug-003) | `POST /users` | 409 on duplicate email | 500 | ❌ | ❌ | High |
| [BUG-004](#bug-004) | `GET /users/{email}` | 404 for unknown user | 500 | ❌ | ❌ | Medium |
| [BUG-005](#bug-005) | `POST /users` | 400 on malformed email | 201, user created | ❌ | ❌ | Medium |
| [BUG-006](#bug-006) | `POST` / `PUT /users/{email}` | 400 when `name` is not a string | 201 / 200 | ❌ | ❌ | Medium |
| [BUG-007](#bug-007) | `POST /users` | 400 when body is not an object | 500 | ❌ | ❌ | Low |

❌ = reproduced, ✅ = behaves as specified

---

## BUG-001
**DELETE does not enforce authentication in `dev`**

- **Spec:** `DELETE /users/{email}` requires the `Authentication` header; responds `401` when it is missing or invalid.
- **Actual (dev):** with no header, or with `Authentication: wrong-token`, the API returns `204` and the user is deleted.
- **Actual (prod):** returns `401 {"error": "Authentication required"}` as expected.
- **Impact:** anyone can delete any user in dev; also breaks the "identical behavior" guarantee between environments.

```bash
curl -X POST localhost:3000/dev/users -H 'Content-Type: application/json' -d '{"name":"A","email":"a@example.com","age":30}'
curl -i -X DELETE localhost:3000/dev/users/a@example.com          # 204 (expected 401)
curl -i localhost:3000/dev/users/a@example.com                     # user is gone
```

**Tests:** `test_delete_user.py::test_delete_user_without_valid_token_returns_401[missing-token]`, `[invalid-token]`

---

## BUG-002
**PUT returns the updated user but does not persist the change**

- **Spec:** `200 — User updated successfully`.
- **Actual:** the `PUT` response body contains the new values, but a following `GET` returns the original user.
- **Impact:** silent data loss — clients are told the update succeeded.

```bash
curl -X POST localhost:3000/dev/users -H 'Content-Type: application/json' -d '{"name":"Orig","email":"p@example.com","age":30}'
curl -X PUT  localhost:3000/dev/users/p@example.com -H 'Content-Type: application/json' -d '{"name":"New","email":"p@example.com","age":31}'
# -> 200 {"name":"New","age":31,...}
curl localhost:3000/dev/users/p@example.com
# -> 200 {"name":"Orig","age":30,...}
```

**Test:** `test_update_user.py::test_update_user_returns_200_and_persists_changes`

---

## BUG-003
**Creating a user with an existing email returns 500 instead of 409**

- **Spec:** `409 — Duplicate email`.
- **Actual:** `500 {"error": "Internal server error"}`. The original record is left intact (no duplicate is stored), so the uniqueness rule holds but the error is unhandled.

**Test:** `test_create_user.py::test_create_user_with_existing_email_returns_409`

---

## BUG-004
**Getting a non-existent user returns 500 instead of 404**

- **Spec:** `404 — User not found`.
- **Actual:** `500 {"error": "Internal server error"}`. Note that `PUT` and `DELETE` on an unknown user correctly return `404`, so only `GET` is affected.

**Test:** `test_get_user.py::test_get_unknown_user_returns_404`

---

## BUG-005
**POST accepts a malformed email**

- **Spec:** `CreateUserRequest.email` is `format: email`; invalid input → `400`.
- **Actual:** `{"email": "not-an-email"}` is stored and returned with `201`.
- **Inconsistency:** `PUT` with the same value correctly returns `400`, so the validation exists but is not applied on create.

**Test:** `test_create_user.py::test_create_user_rejects_invalid_payload[email-bad-format]`

---

## BUG-006
**`name` is not type-checked**

- **Spec:** `name` is `type: string` in both request schemas.
- **Actual:** `{"name": 123, ...}` is accepted (`201` on POST, `200` on PUT) and the response returns `"name": 123`, which also violates the `User` response schema.
- `age` type validation works (`"thirty"` → `400`), so the gap is specific to `name`.

**Tests:** `test_create_user.py::test_create_user_rejects_invalid_payload[name-not-string]`, `test_update_user.py::test_update_user_rejects_invalid_payload[name-not-string]`

---

## BUG-007
**A JSON body that is not an object crashes the server**

- **Spec:** request body is an object (`CreateUserRequest`); invalid input → `400`.
- **Actual:** sending a JSON array (`[]`) returns `500`. Malformed JSON (e.g. `abc`) is handled correctly with `400 {"error": "Invalid JSON body"}`.

**Test:** `test_create_user.py::test_create_user_with_non_object_body_returns_400`
