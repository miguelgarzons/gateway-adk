# FastAPI Hexagonal Architecture (Advanced)

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000/hello

## Endpoints

- Health: `GET /health`
- Docs (Scalar): `GET /docs`
- Zoho webhook: `POST /webhooks/zoho/ticket`

## Webhook -> ADK

El endpoint `POST /webhooks/zoho/ticket` hace dos llamadas al servidor ADK:

1. Crea sesion:
   - `POST /apps/{appName}/users/{userId}/sessions/{sessionId}`
2. Ejecuta agente:
   - `POST /run`

Variables de entorno:

- `ADK_BASE_URL` (default: `http://localhost:8001`)
- `ADK_APP_NAME` (default: `helpdesk_agent`)
- `ADK_TIMEOUT_SECONDS` (default: `20`)
