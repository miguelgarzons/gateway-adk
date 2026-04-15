import json
from typing import Any

from app.domain.ports.agent_client import HelpdeskAgentClient


class ProcessZohoWebhookUseCase:
    def __init__(self, agent_client: HelpdeskAgentClient, app_name: str):
        self.agent_client = agent_client
        self.app_name = app_name

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        ticket_id = str(payload.get("id") or "unknown")
        contact_id = str(
            payload.get("contactId") or payload.get("email") or "anonymous"
        )

        user_id = f"user_{contact_id}"
        session_id = f"ticket_{ticket_id}"

        self.agent_client.create_session(self.app_name, user_id, session_id)

        message = self._build_message(payload)
        run_response = self.agent_client.run(
            self.app_name, user_id, session_id, message
        )

        return {
            "status": "processed",
            "appName": self.app_name,
            "userId": user_id,
            "sessionId": session_id,
            "ticketId": ticket_id,
            "runResponse": run_response,
        }

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
        return (
            "Analiza el siguiente ticket de mesa de ayuda y sugiere la mejor respuesta en espanol, "
            "con pasos claros y accionables para el agente.\n\n"
            f"Contexto del ticket:\n{context_json}"
        )
