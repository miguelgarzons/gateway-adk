import json
import logging
from dataclasses import dataclass
from typing import Any, Callable

from app.domain.ports.agent_client import AgentClientError, HelpdeskAgentClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentTarget:
    base_url: str
    app_name: str


class ProcessZohoWebhookUseCase:
    def __init__(
        self,
        agent_client_factory: Callable[[str], HelpdeskAgentClient],
        target: AgentTarget,
    ):
        self.agent_client_factory = agent_client_factory
        self.target = target

    def build_ack(self, payload: dict[str, Any]) -> dict[str, str]:
        ticket_id = str(payload.get("id") or "unknown")
        identity = payload.get("contactId") or payload.get("email") or ticket_id
        contact_id = str(identity)

        user_id = f"user_{contact_id}"
        session_id = f"ticket_{ticket_id}"

        return {
            "status": "accepted",
            "appName": self.target.app_name,
            "userId": user_id,
            "sessionId": session_id,
            "ticketId": ticket_id,
        }

    def execute(self, payload: dict[str, Any]) -> None:
        ticket_id = str(payload.get("id") or "unknown")
        ack = self.build_ack(payload)
        agent_client: HelpdeskAgentClient = self.agent_client_factory(self.target.base_url)
        user_id = ack["userId"]
        session_id = ack["sessionId"]

        logger.info(
            "Webhook execution start ticketId=%s appName=%s baseUrl=%s userId=%s sessionId=%s",
            ticket_id,
            self.target.app_name,
            self.target.base_url,
            user_id,
            session_id,
        )

        agent_client.create_session(self.target.app_name, user_id, session_id)
        logger.info(
            "Webhook session ensured ticketId=%s appName=%s", ticket_id, self.target.app_name
        )

        message = self._build_message(payload)
        agent_client.run(self.target.app_name, user_id, session_id, message)
        logger.info(
            "Webhook run completed ticketId=%s appName=%s", ticket_id, self.target.app_name
        )

    def execute_safely(self, payload: dict[str, Any]) -> None:
        ticket_id = str(payload.get("id") or "unknown")
        try:
            self.execute(payload)
        except AgentClientError as exc:
            logger.warning(
                "ADK processing failed ticketId=%s error=%s", ticket_id, str(exc)
            )
        except Exception as exc:
            logger.error(
                "Unexpected webhook processing error ticketId=%s error=%s",
                ticket_id,
                str(exc),
            )

    def _build_message(self, payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False)
