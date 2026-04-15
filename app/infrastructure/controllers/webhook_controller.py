from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.application.webhook_use_cases import ProcessZohoWebhookUseCase
from app.domain.ports.agent_client import AgentClientError
from app.infrastructure.dependencies import get_process_zoho_webhook_use_case

router = APIRouter(tags=["webhooks"])


class ZohoTicketWebhookPayload(BaseModel):
    id: str
    subject: str | None = None
    description: str | None = None
    status: str | None = None
    ticketNumber: str | None = None
    contactId: str | None = None
    email: str | None = None
    phone: str | None = None
    channel: str | None = None
    priority: str | None = None
    webUrl: str | None = None
    createdTime: str | None = None
    modifiedTime: str | None = None
    dueDate: str | None = None
    cf: dict[str, Any] = Field(default_factory=dict)
    customFields: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


@router.post(
    "/webhooks/zoho/ticket",
    summary="Procesa webhook de ticket Zoho",
    status_code=status.HTTP_200_OK,
)
def process_zoho_ticket_webhook(
    payload: ZohoTicketWebhookPayload,
    use_case: ProcessZohoWebhookUseCase = Depends(get_process_zoho_webhook_use_case),
):
    try:
        return use_case.execute(payload.model_dump())
    except AgentClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)
        ) from exc
