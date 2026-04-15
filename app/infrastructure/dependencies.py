import os

from app.application.webhook_use_cases import ProcessZohoWebhookUseCase
from app.domain.services import HelloService
from app.application.use_cases import HelloUseCase
from app.infrastructure.clients.adk_http_client import AdkHttpClient
from app.infrastructure.repositories.in_memory_repository import InMemoryHelloRepository


def get_hello_use_case() -> HelloUseCase:
    repo = InMemoryHelloRepository()
    service = HelloService(repo)
    return HelloUseCase(service)


def get_process_zoho_webhook_use_case() -> ProcessZohoWebhookUseCase:
    base_url = os.getenv("ADK_BASE_URL", "http://localhost:8001")
    app_name = os.getenv("ADK_APP_NAME", "helpdesk_agent")
    timeout_seconds = float(os.getenv("ADK_TIMEOUT_SECONDS", "20"))

    agent_client = AdkHttpClient(base_url=base_url, timeout_seconds=timeout_seconds)
    return ProcessZohoWebhookUseCase(agent_client=agent_client, app_name=app_name)
