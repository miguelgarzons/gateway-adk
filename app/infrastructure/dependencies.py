import os

from app.application.webhook_use_cases import ProcessZohoWebhookUseCase
from app.infrastructure.clients.adk_http_client import AdkHttpClient


def get_process_zoho_webhook_use_case() -> ProcessZohoWebhookUseCase:
    base_url = os.getenv("ADK_BASE_URL", "http://localhost:8001")
    app_name = os.getenv("ADK_APP_NAME", "helpdesk_agent")
    timeout_seconds = float(os.getenv("ADK_TIMEOUT_SECONDS", "20"))
    run_timeout_seconds = float(os.getenv("ADK_RUN_TIMEOUT_SECONDS", "60"))
    run_retries = int(os.getenv("ADK_RUN_RETRIES", "1"))

    agent_client = AdkHttpClient(
        base_url=base_url,
        timeout_seconds=timeout_seconds,
        run_timeout_seconds=run_timeout_seconds,
        run_retries=run_retries,
    )
    return ProcessZohoWebhookUseCase(agent_client=agent_client, app_name=app_name)
