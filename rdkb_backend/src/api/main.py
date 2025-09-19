from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi
from starlette.templating import Jinja2Templates

from src.core.config import get_settings
from src.routers import auth as auth_router
from src.routers import devices as devices_router
from src.routers import configs as configs_router
from src.routers import monitoring as monitoring_router
from src.routers import admin as admin_router

settings = get_settings()

tags_metadata = [
    {"name": "Authentication", "description": "Endpoints for login, registration and current user"},
    {"name": "Devices", "description": "Manage FWA devices: register, list, update, delete"},
    {"name": "Configuration", "description": "Manage device configurations"},
    {"name": "Monitoring", "description": "Submit and fetch telemetry"},
    {"name": "Admin", "description": "Administrative operations and stats"},
]

app = FastAPI(
    title=settings.app_name,
    description="RESTful APIs for the RDK-B Fixed Wireless Access platform backend.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
cors = settings.cors()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors.allow_origins,
    allow_credentials=cors.allow_credentials,
    allow_methods=cors.allow_methods,
    allow_headers=cors.allow_headers,
)

# Templates
templates = Jinja2Templates(directory="src/templates")

# Routers
app.include_router(auth_router.router)
app.include_router(devices_router.router)
app.include_router(configs_router.router)
app.include_router(monitoring_router.router)
app.include_router(admin_router.router)

# Health
@app.get("/", summary="Health Check", tags=["Admin"])
def health_check():
    """Simple health check endpoint."""
    return {"message": "Healthy"}

# UI help
@app.get("/help", response_class=HTMLResponse, summary="API Help UI", tags=["Admin"])
def help_page(request: Request):
    """Render an Ocean Professional themed API help page."""
    return templates.TemplateResponse(
        "docs_help.html",
        {"request": request, "title": settings.app_name, "base_url": f"http://{settings.app_host}:{settings.app_port}"},
    )


def custom_openapi():
    """Customize OpenAPI schema with additional metadata."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.app_name,
        version="1.0.0",
        description="RESTful APIs for device configuration, monitoring, authentication, and admin operations.",
        routes=app.routes,
        tags=tags_metadata,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
