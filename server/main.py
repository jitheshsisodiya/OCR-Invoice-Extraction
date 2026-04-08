"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from core.logging import setup_logging
from db.session import init_db
from ocr.registry import init_default_engines
from bundled import configure_environment

# Import all models so SQLAlchemy can create tables
from db.models.document import Document, DocumentPage  # noqa: F401
from db.models.work_session import WorkSession  # noqa: F401
from db.models.clip_mapping import ClipMapping  # noqa: F401
from db.models.validation import ValidationRecord  # noqa: F401

# Route modules
from api.v1 import documents, sessions, clips, extractions, validations, form_extraction, summarize, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(debug=settings.debug)
    # Configure Tesseract + Poppler paths (bundled or system)
    configure_environment()
    settings.ensure_dirs()
    init_db(settings.database_url)
    init_default_engines(
        tesseract_cmd=None,   # already set by configure_environment() via pytesseract
        easyocr_model_dir=settings.easyocr_model_dir,
    )
    yield


app = FastAPI(
    title="OCR Invoice Extraction API",
    description="Local OCR server for the Excel add-in. Extracts text, tables, and form fields from documents.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow Task Pane (localhost:3000) to call this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(documents.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(clips.router, prefix="/api/v1")
app.include_router(extractions.router, prefix="/api/v1")
app.include_router(validations.router, prefix="/api/v1")
app.include_router(form_extraction.router, prefix="/api/v1")
app.include_router(summarize.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
