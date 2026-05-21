import os

from app.application.webhook_use_cases import (
    AgentTarget,
    ProcessZohoWebhookUseCase,
)
from app.infrastructure.clients.adk_http_client import AdkHttpClient


def get_process_zoho_webhook_use_case() -> ProcessZohoWebhookUseCase:
    timeout_seconds = float(os.getenv("ADK_TIMEOUT_SECONDS", "20"))
    run_timeout_seconds = float(os.getenv("ADK_RUN_TIMEOUT_SECONDS", "60"))
    run_retries = int(os.getenv("ADK_RUN_RETRIES", "1"))

    categorizador_base_url = os.getenv("ADK_CATEGORIZADOR_BASE_URL", "").strip()
    if not categorizador_base_url:
        raise RuntimeError(
            "ADK_CATEGORIZADOR_BASE_URL is required but not set"
        )

    categorizador_app_name = os.getenv(
        "ADK_CATEGORIZADOR_APP_NAME", "categorizador_agent"
    )

    def build_agent_client(target_base_url: str) -> AdkHttpClient:
        return AdkHttpClient(
            base_url=target_base_url,
            timeout_seconds=timeout_seconds,
            run_timeout_seconds=run_timeout_seconds,
            run_retries=run_retries,
        )

    target = AgentTarget(
        base_url=categorizador_base_url,
        app_name=categorizador_app_name,
    )

    return ProcessZohoWebhookUseCase(
        agent_client_factory=build_agent_client,
        target=target,
        
    )
