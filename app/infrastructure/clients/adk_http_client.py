from typing import Any
from urllib.parse import quote

import httpx

from app.domain.ports.agent_client import AgentClientError, HelpdeskAgentClient


class AdkHttpClient(HelpdeskAgentClient):
    def __init__(self, base_url: str, timeout_seconds: float = 20.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def create_session(self, app_name: str, user_id: str, session_id: str) -> None:
        url = (
            f"{self.base_url}/apps/{quote(app_name, safe='')}/users/{quote(user_id, safe='')}"
            f"/sessions/{quote(session_id, safe='')}"
        )

        try:
            response = httpx.post(url, json={}, timeout=self.timeout_seconds)
        except httpx.RequestError as exc:
            raise AgentClientError(
                f"No fue posible crear sesion en ADK: {exc}"
            ) from exc

        if response.status_code in (200, 201, 204, 409):
            return

        raise AgentClientError(
            "ADK rechazo la creacion de sesion "
            f"({response.status_code}): {response.text[:500]}"
        )

    def run(
        self, app_name: str, user_id: str, session_id: str, message: str
    ) -> dict[str, Any]:
        url = f"{self.base_url}/run"
        payload = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [{"text": message}],
            },
        }

        try:
            response = httpx.post(url, json=payload, timeout=self.timeout_seconds)
        except httpx.RequestError as exc:
            raise AgentClientError(
                f"No fue posible ejecutar /run en ADK: {exc}"
            ) from exc

        if not response.is_success:
            raise AgentClientError(
                f"ADK rechazo /run ({response.status_code}): {response.text[:500]}"
            )

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()

        return {"raw": response.text}
