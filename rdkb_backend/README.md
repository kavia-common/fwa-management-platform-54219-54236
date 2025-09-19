# RDKB Backend (FastAPI)

This service provides RESTful APIs for:
- Authentication (OAuth2 password flow)
- Devices (CRUD)
- Configuration (device config upsert/list)
- Monitoring (telemetry submit/list)
- Admin (DB init, seed admin, stats)

Run locally:
- Install requirements: pip install -r requirements.txt
- Set environment variables (.env) as per .env.example
- Start: uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

OpenAPI:
- /docs (Swagger UI)
- /redoc
- /help (Ocean Professional themed help page)
