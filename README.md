# Gateway ADK API

Servicio FastAPI para integrar tickets de Zoho Desk con un agente ADK.

## Objetivo

Este servicio recibe webhooks de tickets, normaliza el contexto y lo envia al backend ADK para que el agente genere una respuesta sugerida.

## Ejecucion local

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## Endpoints

- `GET /health`: estado del servicio.
- `GET /docs`: documentacion interactiva (Scalar/OpenAPI).
- `POST /webhooks/zoho/ticket`: encola el procesamiento del ticket y responde de inmediato (asincrono).

## Documentacion API

- El endpoint `POST /webhooks/zoho/ticket` incluye un ejemplo completo de payload Zoho Desk en Scalar.
- La documentacion del webhook se mantiene separada del controlador en `app/infrastructure/docs/webhook_docs.py`.

## Flujo Zoho -> ADK

Cuando llega `POST /webhooks/zoho/ticket`, el servicio responde `202 Accepted` y luego procesa en segundo plano:

1. Creacion (o reutilizacion) de sesion en ADK:
   - `POST /apps/{appName}/users/{userId}/sessions/{sessionId}`
2. Ejecucion del agente:
   - `POST /run`

El mensaje enviado a ADK incluye informacion del ticket (estado, prioridad, descripcion, canal, fechas y campos personalizados).
El endpoint no espera la respuesta de ADK para responder al cliente.

## Variables de entorno

- `ADK_BASE_URL` (default: `http://localhost:8001`)
- `ADK_APP_NAME` (default: `helpdesk_agent`)
- `ADK_TIMEOUT_SECONDS` (default: `20`)

## Despliegue en Cloud Run

La imagen Docker expone la app en el puerto definido por `PORT` (Cloud Run usa `8080` por defecto).
El pipeline de GitHub Actions en `.github/workflows/deploy-cloud-run.yml` construye la imagen y despliega el servicio `gateway-adk`.
