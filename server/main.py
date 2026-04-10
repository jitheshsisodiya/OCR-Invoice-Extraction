"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from config import settings
from core.logging import setup_logging
from db.session import init_db
from ocr.registry import init_default_engines
from bundled import configure_environment, get_taskpane_dir

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

# Allow Task Pane to call this server (dev on :3000, production served from :7432)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://localhost:3000",
        "http://localhost:7432",
        "https://localhost:7432",
        "null",          # file:// origin used by some Office.js versions
    ],
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


# Serve the built Task Pane static files at /taskpane/
# This allows the production installer manifest to reference http://localhost:7432/taskpane/
_taskpane_dir = get_taskpane_dir()
if _taskpane_dir:
    app.mount("/taskpane", StaticFiles(directory=str(_taskpane_dir), html=True), name="taskpane")


if __name__ == "__main__":
    import multiprocessing
    # Required for PyInstaller frozen executables on all platforms
    multiprocessing.freeze_support()

    # On Windows, Python 3.8+ defaults to ProactorEventLoop which breaks uvicorn.
    # Force SelectorEventLoop so that uvicorn works correctly in the bundled .exe.
    import sys, asyncio
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    import uvicorn
    # When frozen by PyInstaller, pass the app object directly — the
    # "main:app" string form requires dynamic import which fails in a bundle.
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=False,        # reload requires source files; never use in bundle
    )
