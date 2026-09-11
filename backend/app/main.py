from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes.documents import router as documents_router
from backend.app.core.database import Base, engine


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Document Intelligence Platform",
    version="1.0.0"
)


# API routes
app.include_router(documents_router)


# Frontend paths
BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"


# Serve CSS and JavaScript
app.mount(
    "/static",
    StaticFiles(
        directory=FRONTEND_DIR / "static"
    ),
    name="static"
)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    dashboard_file = (
        FRONTEND_DIR
        / "templates"
        / "dashboard.html"
    )

    return dashboard_file.read_text(
        encoding="utf-8"
    )


@app.get(
    "/document/{document_name}",
    response_class=HTMLResponse
)
def document_result(document_name: str):
    result_file = (
        FRONTEND_DIR
        / "templates"
        / "document_result.html"
    )

    return result_file.read_text(
        encoding="utf-8"
    )


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy"
    }