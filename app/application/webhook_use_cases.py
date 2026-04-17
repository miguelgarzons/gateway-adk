import json
import logging
from typing import Any

from app.domain.ports.agent_client import AgentClientError, HelpdeskAgentClient

logger = logging.getLogger(__name__)


class ProcessZohoWebhookUseCase:
    def __init__(self, agent_client: HelpdeskAgentClient, app_name: str):
        self.agent_client = agent_client
        self.app_name = app_name

    def build_ack(self, payload: dict[str, Any]) -> dict[str, str]:
        ticket_id = str(payload.get("id") or "unknown")
        identity = payload.get("contactId") or payload.get("email") or ticket_id
        contact_id = str(identity)

        user_id = f"user_{contact_id}"
        session_id = f"ticket_{ticket_id}"

        return {
            "status": "accepted",
            "appName": self.app_name,
            "userId": user_id,
            "sessionId": session_id,
            "ticketId": ticket_id,
        }

    def execute(self, payload: dict[str, Any]) -> None:
        ack = self.build_ack(payload)
        user_id = ack["userId"]
        session_id = ack["sessionId"]

        self.agent_client.create_session(self.app_name, user_id, session_id)

        message = self._build_message(payload)
        self.agent_client.run(self.app_name, user_id, session_id, message)

    def execute_safely(self, payload: dict[str, Any]) -> None:
        ticket_id = str(payload.get("id") or "unknown")
        try:
            self.execute(payload)
            logger.info("ADK processing completed ticketId=%s", ticket_id)
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
        cf = payload.get("cf") or {}

        context = {
            "ticketId": payload.get("id"),
            "ticketNumber": payload.get("ticketNumber"),
            "status": payload.get("status"),
            "subject": payload.get("subject"),
            "description": payload.get("description"),
            "channel": payload.get("channel"),
            "priority": payload.get("priority"),
            "contactId": payload.get("contactId"),
            "email": payload.get("email"),
            "phone": payload.get("phone"),
            "webUrl": payload.get("webUrl"),
            "createdTime": payload.get("createdTime"),
            "modifiedTime": payload.get("modifiedTime"),
            "dueDate": payload.get("dueDate"),
            "programa": cf.get("cf_programa"),
            "modalidad": cf.get("cf_modalidad"),
            "periodo": cf.get("cf_periodo"),
            "subCategorias": cf.get("cf_sub_categorias"),
            "categoria": cf.get("cf_categoria"),
            "numeroDocumento": cf.get("cf_numero_de_documento"),
            "observaciones": cf.get("cf_observaciones"),
        }

        context_json = json.dumps(context, ensure_ascii=False, indent=2)
        return f"Contexto del ticket:\n{context_json}"
