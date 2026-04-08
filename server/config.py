"""Application settings via pydantic-settings."""
from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    host: str = "127.0.0.1"
    port: int = 7432
    debug: bool = False

    # Storage
    upload_dir: Path = Path("../data/uploads")
    thumbnail_dir: Path = Path("../data/thumbnails")
    export_dir: Path = Path("../data/exports")

    # Database
    database_url: str = "sqlite:///./ocr_invoice.db"

    # OCR
    default_ocr_engine: str = "tesseract"
    tesseract_cmd: str = "tesseract"
    ocr_dpi: int = 300
    cross_validate_ocr: bool = True
    easyocr_model_dir: str | None = None

    # AI
    anthropic_api_key: str = ""

    def ensure_dirs(self) -> None:
        for d in [self.upload_dir, self.thumbnail_dir, self.export_dir]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
