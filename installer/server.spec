# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for the OCR Invoice Extraction server.
# Run from the repo root on Windows:
#   pyinstaller installer/server.spec
#
# Pre-requisites:
#   server\tesseract\    - tesseract.exe + DLLs  (fetch_windows_binaries.ps1)
#   server\poppler\      - bin\pdftoppm.exe etc.  (fetch_windows_binaries.ps1)
#   server\tessdata\     - eng.traineddata         (already in repo)
#   taskpane\dist\       - built by: npm run build (build_server.bat step 2)

import os
import sys
from pathlib import Path

# Allow running spec from any directory
SPEC_DIR   = Path(SPECFILE).parent          # installer/
REPO_ROOT  = SPEC_DIR.parent               # repo root
SERVER_DIR = REPO_ROOT / "server"

# ── Data bundles ──────────────────────────────────────────────────────────────
datas = [
    # Tesseract trained data
    (str(SERVER_DIR / "tessdata"),  "tessdata"),
    # Poppler binaries (bin/ + lib/)
    (str(SERVER_DIR / "poppler"),   "poppler"),
    # Built Task Pane (served as static files by FastAPI)
    (str(REPO_ROOT / "taskpane" / "dist"), "taskpane"),
]

# Tesseract executable + DLLs — only present on Windows build machine
tesseract_dir = SERVER_DIR / "tesseract"
if tesseract_dir.exists():
    datas.append((str(tesseract_dir), "tesseract"))

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    [str(SERVER_DIR / "main.py")],
    pathex=[str(SERVER_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # uvicorn internal modules not auto-detected
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        # OCR / ML
        "easyocr",
        "camelot",
        "PIL",
        "cv2",
        # pydantic v2 validators
        "pydantic.deprecated.class_validators",
        "pydantic.deprecated.config",
        "pydantic.deprecated.tools",
        # SQLAlchemy dialects
        "sqlalchemy.dialects.sqlite",
        # multipart (FastAPI file uploads)
        "multipart",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",        # not needed, saves ~10 MB
        "matplotlib",
        "notebook",
        "IPython",
    ],
    noarchive=False,
    optimize=1,
)

# Collect all EasyOCR and pytesseract package data
from PyInstaller.utils.hooks import collect_all
for pkg in ("easyocr", "pytesseract"):
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
    a.datas     += pkg_datas
    a.binaries  += pkg_binaries
    a.hiddenimports += pkg_hiddenimports

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="server",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,            # keep console visible for debugging; set False for silent
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,               # TODO: set to installer/assets/installer_icon.ico on Windows
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="server",
    distpath=str(REPO_ROOT / "dist"),
)
