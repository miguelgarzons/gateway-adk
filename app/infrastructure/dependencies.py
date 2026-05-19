import os

from app.application.webhook_use_cases import (
    AgentRouteRule,
    AgentTarget,
    ProcessZohoWebhookUseCase,
)
from app.infrastructure.clients.adk_http_client import AdkHttpClient


def get_process_zoho_webhook_use_case() -> ProcessZohoWebhookUseCase:
    timeout_seconds = float(os.getenv("ADK_TIMEOUT_SECONDS", "20"))
    run_timeout_seconds = float(os.getenv("ADK_RUN_TIMEOUT_SECONDS", "60"))
    run_retries = int(os.getenv("ADK_RUN_RETRIES", "1"))

    def build_agent_client(target_base_url: str) -> AdkHttpClient:
        return AdkHttpClient(
            base_url=target_base_url,
            timeout_seconds=timeout_seconds,
            run_timeout_seconds=run_timeout_seconds,
            run_retries=run_retries,
        )

    routes: list[AgentRouteRule] = []
    verificacion_base_url = os.getenv("ADK_VERIFICACION_ACADEMICA_BASE_URL", "").strip()
    if verificacion_base_url:
        verificacion_app_name = os.getenv(
            "ADK_VERIFICACION_ACADEMICA_APP_NAME", "verificacion_academica_agent"
        )
        routes.append(
            AgentRouteRule(
                solicitud="ACADEMICA",
                categoria="CERTIFICACIONES Y VERIFICACIONES",
                sub_categorias="VERIFICACION ACADEMICA",
                target=AgentTarget(
                    base_url=verificacion_base_url,
                    app_name=verificacion_app_name,
                ),
            )
        )

    return ProcessZohoWebhookUseCase(
        agent_client_factory=build_agent_client,
        routes=routes,
    )
