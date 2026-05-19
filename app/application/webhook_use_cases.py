import json
import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Callable

from app.domain.ports.agent_client import AgentClientError, HelpdeskAgentClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentTarget:
    base_url: str
    app_name: str


@dataclass(frozen=True)
class AgentRouteRule:
    solicitud: str
    categoria: str
    sub_categorias: str
    target: AgentTarget

    def matches(self, solicitud: str, categoria: str, sub_categorias: str) -> bool:
        return (
            _normalize_text(self.solicitud) == _normalize_text(solicitud)
            and _normalize_text(self.categoria) == _normalize_text(categoria)
            and _normalize_text(self.sub_categorias) == _normalize_text(sub_categorias)
        )


class ProcessZohoWebhookUseCase:
    def __init__(
        self,
        agent_client_factory: Callable[[str], HelpdeskAgentClient],
        routes: list[AgentRouteRule] | None = None,
    ):
        self.agent_client_factory = agent_client_factory
        self.routes = routes or []

    def build_ack(self, payload: dict[str, Any]) -> dict[str, str]:
        ticket_id = str(payload.get("id") or "unknown")
        identity = payload.get("contactId") or payload.get("email") or ticket_id
        contact_id = str(identity)

        user_id = f"user_{contact_id}"
        session_id = f"ticket_{ticket_id}"

        return {
            "status": "accepted",
            "userId": user_id,
            "sessionId": session_id,
            "ticketId": ticket_id,
        }

    def execute(self, payload: dict[str, Any]) -> None:
        target = self._resolve_target(payload)
        ticket_id = str(payload.get("id") or "unknown")

        if target is None:
            logger.info(
                "Ticket skipped ticketId=%s reason=no matching route",
                ticket_id,
            )
            return

        ack = self.build_ack(payload)
        agent_client: HelpdeskAgentClient = self.agent_client_factory(target.base_url)
        user_id = ack["userId"]
        session_id = ack["sessionId"]

        logger.info(
            "Webhook execution start ticketId=%s appName=%s baseUrl=%s userId=%s sessionId=%s",
            ticket_id,
            target.app_name,
            target.base_url,
            user_id,
            session_id,
        )

        agent_client.create_session(target.app_name, user_id, session_id)
        logger.info(
            "Webhook session ensured ticketId=%s appName=%s", ticket_id, target.app_name
        )

        message = self._build_message(payload)
        agent_client.run(target.app_name, user_id, session_id, message)
        logger.info(
            "Webhook run completed ticketId=%s appName=%s", ticket_id, target.app_name
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

    def _resolve_target(self, payload: dict[str, Any]) -> AgentTarget | None:
        request_meta = self._extract_request_meta(payload)
        solicitud = request_meta["solicitud"]
        categoria = request_meta["categoria"]
        sub_categorias = request_meta["sub_categorias"]

        for route in self.routes:
            if route.matches(solicitud, categoria, sub_categorias):
                logger.info(
                    "Webhook route matched solicitud=%s categoria=%s subCategorias=%s appName=%s",
                    solicitud,
                    categoria,
                    sub_categorias,
                    route.target.app_name,
                )
                return route.target

        logger.info(
            "Webhook no matching route ticketId=%s solicitud=%s categoria=%s subCategorias=%s",
            payload.get("id", "?"),
            solicitud,
            categoria,
            sub_categorias,
        )
        return None

    def _extract_request_meta(self, payload: dict[str, Any]) -> dict[str, str]:
        custom_fields = payload.get("customFields") or {}
        cf = payload.get("cf") or {}

        solicitud = _first_non_empty(
            payload.get("solicitud"),
            custom_fields.get("SOLICITUD"),
            custom_fields.get("SOLICITUD*"),
            cf.get("cf_solictud"),
            cf.get("cf_solicitud"),
        )
        categoria = _first_non_empty(
            payload.get("categoria"),
            custom_fields.get("CATEGORIA"),
            custom_fields.get("CATEGORIA*"),
            cf.get("cf_categoria"),
        )
        sub_categorias = _first_non_empty(
            payload.get("subCategorias"),
            payload.get("subCategory"),
            custom_fields.get("SUB CATEGORIAS"),
            custom_fields.get("SUB CATEGORIAS*"),
            custom_fields.get("SUB CATEGORIA"),
            cf.get("cf_sub_categorias"),
        )

        return {
            "solicitud": solicitud,
            "categoria": categoria,
            "sub_categorias": sub_categorias,
        }


def _first_non_empty(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    normalized = re.sub(r"[^A-Za-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip().upper()
    return normalized
