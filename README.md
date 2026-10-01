# User Management API — E2E Test Suite

End-to-end tests for the User Management API v1.0, written with **Python + pytest + Playwright** (`APIRequestContext`).
The same suite runs against the `dev` and `prod` environments, in parallel, on GitHub Actions.

- Bugs found: [BUGS.md](BUGS.md)
- API contract: [spec/sdet_challenge_api.yml](spec/sdet_challenge_api.yml)
- Test reports: [reports/](reports/)

## Expected results

The API has known defects, so **both CI jobs are expected to fail**. Assertions follow the spec and are not relaxed to make the pipeline green — every failure maps to a bug in [BUGS.md](BUGS.md).

| Environment | Passed | Failed | Failing because of |
|-------------|:------:|:------:|--------------------|
| `dev` | 23 / 32 | 9 | BUG-001 … BUG-007 |
| `prod` | 25 / 32 | 7 | BUG-002 … BUG-007 (auth on DELETE works in prod) |

## Run locally

Requires Docker and Python 3.12+.

```bash
docker run -d -p 3000:3000 ghcr.io/danielsilva-loanpro/sdet-interview-challenge:latest

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest --env dev                   # or: --env prod
pytest --env prod --html=reports/prod/report.html --self-contained-html
```

No browser download is needed — only Playwright's HTTP client is used.

| Option | Env var | Default |
|--------|---------|---------|
| `--env` | `TARGET_ENV` | `dev` |
| `--api-url` | `API_URL` | `http://localhost:3000` |
| — | `API_TOKEN` | `mysecrettoken` |

## Project layout

```
spec/                     OpenAPI contract (source of truth for response schemas)
tests/
  api/
    users_client.py       Thin client: one method per endpoint
    schemas.py            Validates responses against the spec's components/schemas
    user_factory.py       Valid payload builder + invalid-field cases
    settings.py           Environment configuration
  conftest.py             Fixtures: Playwright request context, clients, test users, cleanup
  test_list_users.py      GET    /users
  test_create_user.py     POST   /users
  test_get_user.py        GET    /users/{email}
  test_update_user.py     PUT    /users/{email}
  test_delete_user.py     DELETE /users/{email}
  test_environment_isolation.py
.github/workflows/
  e2e.yml                 Entry point: dev and prod jobs in parallel
  run-e2e.yml             Reusable job: start API, run suite, publish reports
```

## Test design

Coverage is driven by the spec: **every documented status code of every operation has at least one test**,
plus the validation rules declared in the request schemas, plus environment isolation.

| Operation | Covered responses | Tests |
|-----------|-------------------|-------|
| `GET /users` | 200 (array of `User`) | 1 |
| `POST /users` | 201 (+ persisted, age boundaries 1/150), 400 (each validation rule, non-object body), 409 | 5 functions / 13 cases |
| `GET /users/{email}` | 200, 404 | 2 |
| `PUT /users/{email}` | 200 (+ persisted), 400 (each validation rule), 404, 409 | 4 functions / 11 cases |
| `DELETE /users/{email}` | 204 (+ removed), 401 (missing / invalid token), 404 | 3 functions / 4 cases |
| Isolation | user created in one env is not visible in the other | 1 |

**32 cases per environment.** Design choices:

- **Assert only what the spec defines.** E.g. empty `name` or very long strings are not tested because the spec sets no `minLength`/`maxLength`.
- **Validation rules are one parametrized table** (`INVALID_FIELDS`) shared by POST and PUT, since both request schemas declare the same rules.
- **Every response is checked against the full contract**: status code, `Content-Type: application/json` and the spec's own schema (`jsonschema` + the YAML, not hand-copied); `204` must have an empty body.
- **Persistence is verified with a follow-up read**, not just from the write's response — this is what exposed BUG-002.
- **Each test creates its own data** with a unique email and deletes it afterwards, so tests are independent and order-agnostic.

## CI

`.github/workflows/e2e.yml` calls the reusable workflow twice — `dev` and `prod` — with no dependency between them,
so they run in parallel and a failing environment never blocks the other. Each job:

1. Starts the API image as a service container
2. Waits for it to respond
3. Runs the suite with `TARGET_ENV` set to its environment
4. Writes a pass/fail summary to the job page and uploads the HTML + JUnit reports as artifacts (`test-report-dev`, `test-report-prod`)

## Reports

Each CI run produces a self-contained HTML report (pytest-html) and a JUnit XML per environment.
A sample from a CI run is committed in [`reports/`](reports/) so it can be reviewed without downloading artifacts:

| Environment | HTML | JUnit |
|-------------|------|-------|
| `dev` | [reports/dev/report.html](reports/dev/report.html) | [reports/dev/junit.xml](reports/dev/junit.xml) |
| `prod` | [reports/prod/report.html](reports/prod/report.html) | [reports/prod/junit.xml](reports/prod/junit.xml) |

GitHub shows HTML files as source; download the file and open it in a browser to see the rendered report.
