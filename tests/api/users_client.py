from playwright.sync_api import APIRequestContext, APIResponse


class UsersClient:
    """Thin wrapper over the /{env}/users endpoints so tests read like the spec."""

    def __init__(self, request: APIRequestContext, env: str):
        self._request = request
        self.env = env

    def _url(self, email: str | None = None) -> str:
        path = f"/{self.env}/users"
        return f"{path}/{email}" if email is not None else path

    def list_all(self) -> APIResponse:
        return self._request.get(self._url())

    def create(self, payload: dict | list) -> APIResponse:
        return self._request.post(self._url(), data=payload)

    def get(self, email: str) -> APIResponse:
        return self._request.get(self._url(email))

    def update(self, email: str, payload: dict) -> APIResponse:
        return self._request.put(self._url(email), data=payload)

    def delete(self, email: str, token: str | None = None) -> APIResponse:
        headers = {"Authentication": token} if token is not None else {}
        return self._request.delete(self._url(email), headers=headers)
