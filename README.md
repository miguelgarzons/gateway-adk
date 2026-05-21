# Gateway ADK API

Servicio FastAPI para integrar tickets de Zoho Desk con un agente ADK categorizador.

## Objetivo

Este servicio recibe webhooks de tickets y reenvia el payload al backend ADK categorizador para que el agente genere una respuesta sugerida.

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
El payload del webhook se reenvia a ADK en el mismo formato JSON recibido, sin transformacion de campos.

## Destino unico

Todos los tickets se envian al agente categorizador configurado via `ADK_CATEGORIZADOR_BASE_URL`.

### Variables de entorno

| Variable | Default | Descripcion |
|---|---|---|
| `ADK_CATEGORIZADOR_BASE_URL` | **requerido** | URL del agente categorizador |
| `ADK_CATEGORIZADOR_APP_NAME` | `categorizador_agent` | Nombre de la app del agente categorizador |
| `ADK_TIMEOUT_SECONDS` | `20` | Timeout para creacion de sesion |
| `ADK_RUN_TIMEOUT_SECONDS` | `60` | Timeout para ejecucion del agente |
| `ADK_RUN_RETRIES` | `1` | Reintentos ante timeout de lectura en /run |

## Despliegue en Cloud Run

La imagen Docker expone la app en el puerto definido por `PORT` (Cloud Run usa `8080` por defecto).
El pipeline de GitHub Actions en `.github/workflows/deploy-cloud-run.yml` construye la imagen y despliega el servicio `gateway-adk`.
