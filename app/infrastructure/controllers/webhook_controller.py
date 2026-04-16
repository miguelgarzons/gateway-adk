import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Body, Depends, status
from pydantic import BaseModel, ConfigDict, Field

from app.application.webhook_use_cases import ProcessZohoWebhookUseCase
from app.infrastructure.dependencies import get_process_zoho_webhook_use_case
from app.infrastructure.docs.webhook_docs import (
    ZOHO_TICKET_WEBHOOK_ACCEPTED_RESPONSE_EXAMPLE,
    ZOHO_TICKET_WEBHOOK_OPENAPI_EXAMPLES,
)

router = APIRouter(tags=["webhooks"])
logger = logging.getLogger(__name__)


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


class ZohoTicketWebhookAcceptedResponse(BaseModel):
    status: str
    appName: str
    userId: str
    sessionId: str
    ticketId: str


@router.post(
    "/webhooks/zoho/ticket",
    summary="Encola procesamiento asincrono de webhook Zoho",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ZohoTicketWebhookAcceptedResponse,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": "Webhook aceptado para procesamiento asincrono.",
            "content": {
                "application/json": {
                    "example": ZOHO_TICKET_WEBHOOK_ACCEPTED_RESPONSE_EXAMPLE
                }
            },
        }
    },
)
def process_zoho_ticket_webhook(
    background_tasks: BackgroundTasks,
    payload: ZohoTicketWebhookPayload = Body(
        ...,
        openapi_examples=ZOHO_TICKET_WEBHOOK_OPENAPI_EXAMPLES,
        description=(
            "Payload del ticket enviado por Zoho Desk. Soporta payload minimo "
            "con solo 'id' o payload completo del ticket."
        ),
    ),
    use_case: ProcessZohoWebhookUseCase = Depends(get_process_zoho_webhook_use_case),
) -> ZohoTicketWebhookAcceptedResponse:
    payload_data = payload.model_dump()
    logger.info("Zoho webhook received payload=%s", payload_data)
    ack = use_case.build_ack(payload_data)
    logger.info(
        "Zoho webhook accepted ticketId=%s sessionId=%s userId=%s",
        ack["ticketId"],
        ack["sessionId"],
        ack["userId"],
    )
    background_tasks.add_task(use_case.execute_safely, payload_data)
    return ZohoTicketWebhookAcceptedResponse(**ack)
