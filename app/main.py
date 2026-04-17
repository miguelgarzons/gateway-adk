import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.infrastructure.controllers.health_controller import router as health_router
from app.infrastructure.controllers.webhook_controller import router as webhook_router

logger = logging.getLogger("uvicorn.error")

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


@app.middleware("http")
async def log_incoming_requests(request: Request, call_next):
    body_text = ""
    content_type = request.headers.get("content-type", "")
    if request.method in {"POST", "PUT", "PATCH"} and (
        "application/json" in content_type or request.url.path.startswith("/docs")
    ):
        raw_body = await request.body()
        body_text = raw_body.decode("utf-8", errors="replace")[:4000]

    if body_text:
        logger.info(
            "Incoming request method=%s path=%s userAgent=%s contentType=%s body=%s",
            request.method,
            request.url.path,
            request.headers.get("user-agent", ""),
            content_type,
            body_text,
        )

    response = await call_next(request)
    return response


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
