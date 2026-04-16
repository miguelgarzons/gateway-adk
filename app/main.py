from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.infrastructure.controllers.health_controller import router as health_router
from app.infrastructure.controllers.webhook_controller import router as webhook_router

app = FastAPI(
    title="Gateway ADK API",
    version="1.0.0",
    description=(
        "Servicio de integracion para recibir webhooks de Zoho Desk y "
        "enviar el contexto del ticket al agente ADK."
    ),
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
)


@app.get("/docs", include_in_schema=False)
def scalar_docs() -> HTMLResponse:
    return HTMLResponse(
        """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
    <title>Gateway ADK API - Scalar</title>
  </head>
  <body>
    <script
      id=\"api-reference\"
      data-url=\"/openapi.json\"
      data-theme=\"saturn\"
    ></script>
    <script src=\"https://cdn.jsdelivr.net/npm/@scalar/api-reference\"></script>
  </body>
</html>
        """.strip()
    )


app.include_router(health_router)
app.include_router(webhook_router)
