"""
Resolve paths for bundled binaries (Tesseract, Poppler) at runtime.

When running as a PyInstaller .exe, all bundled files live under sys._MEIPASS.
When running normally (dev/Linux), fall back to system paths.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path


def _base_dir() -> Path:
    """Return the directory containing bundled assets."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running inside a PyInstaller bundle
        return Path(sys._MEIPASS)
    # Running in normal Python — assets are in the server/ directory
    return Path(__file__).parent


def get_tessdata_dir() -> Path:
    """Return the path to the tessdata directory."""
    bundled = _base_dir() / "tessdata"
    if bundled.exists():
        return bundled
    # System fallback — common locations
    for candidate in [
        Path("/usr/share/tesseract-ocr/5/tessdata"),
        Path("/usr/share/tesseract-ocr/4.00/tessdata"),
        Path("/usr/local/share/tessdata"),
        Path("C:/Program Files/Tesseract-OCR/tessdata"),
        Path("C:/Program Files (x86)/Tesseract-OCR/tessdata"),
    ]:
        if candidate.exists():
            return candidate
    return bundled  # return bundled path even if not found yet


def get_tesseract_cmd() -> str:
    """Return the path to the tesseract executable."""
    # Bundled Windows tesseract.exe (inside PyInstaller bundle)
    bundled_exe = _base_dir() / "tesseract" / "tesseract.exe"
    if bundled_exe.exists():
        return str(bundled_exe)

    # System tesseract
    import shutil
    system_tess = shutil.which("tesseract")
    if system_tess:
        return system_tess

    # Common Windows install paths
    for candidate in [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]:
        if Path(candidate).exists():
            return candidate

    return "tesseract"  # hope it's on PATH


def get_poppler_bin_dir() -> Path | None:
    """Return the directory containing Poppler executables, or None to use PATH."""
    bundled = _base_dir() / "poppler" / "bin"
    if bundled.exists() and any(bundled.iterdir()):
        return bundled

    import shutil
    if shutil.which("pdftoppm"):
        return None  # already on PATH

    return None


def configure_environment() -> None:
    """
    Set environment variables so that Tesseract and Poppler work correctly
    regardless of whether we are bundled or in a dev environment.
    Called once at server startup.
    """
    # ── Tesseract ──────────────────────────────────────────────────────────
    tessdata = get_tessdata_dir()
    os.environ["TESSDATA_PREFIX"] = str(tessdata)

    import pytesseract
    tess_cmd = get_tesseract_cmd()
    pytesseract.pytesseract.tesseract_cmd = tess_cmd

    # ── Poppler ───────────────────────────────────────────────────────────
    poppler_bin = get_poppler_bin_dir()
    if poppler_bin:
        # Prepend to PATH so pdf2image finds pdftoppm
        current_path = os.environ.get("PATH", "")
        os.environ["PATH"] = str(poppler_bin) + os.pathsep + current_path
