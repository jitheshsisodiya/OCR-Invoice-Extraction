@echo off
REM ============================================================
REM Build the Python FastAPI server into a standalone directory
REM using PyInstaller.  Run this script from the REPO ROOT on
REM Windows after placing the required binaries (see below).
REM
REM Required before running:
REM   server\tessdata\       - eng.traineddata, osd.traineddata
REM                            (already present in repo)
REM   server\poppler\bin\    - pdftoppm.exe, pdfinfo.exe, etc.
REM                            Run: powershell scripts\fetch_windows_binaries.ps1
REM   server\tesseract\      - tesseract.exe + all DLLs
REM                            Run: powershell scripts\fetch_windows_binaries.ps1
REM
REM Output: dist\server\   (used by Inno Setup build.iss)
REM ============================================================
setlocal

echo ============================================================
echo  OCR Invoice Extraction - Server Build
echo ============================================================

REM ── [1/5] Verify required binaries ───────────────────────────────────────────
echo [1/5] Verifying required binaries...
if not exist "server\tessdata\eng.traineddata" (
    echo ERROR: server\tessdata\eng.traineddata not found.
    echo        Run: powershell scripts\fetch_windows_binaries.ps1
    exit /b 1
)
if not exist "server\poppler\bin\pdftoppm.exe" (
    echo ERROR: server\poppler\bin\pdftoppm.exe not found.
    echo        Run: powershell scripts\fetch_windows_binaries.ps1
    exit /b 1
)
if not exist "server\tesseract\tesseract.exe" (
    echo ERROR: server\tesseract\tesseract.exe not found.
    echo        Run: powershell scripts\fetch_windows_binaries.ps1
    exit /b 1
)

REM ── [2/5] Build task pane (must be done before server so we can embed it) ─────
echo [2/5] Building Task Pane...
if not exist "taskpane\node_modules" (
    echo   Installing npm packages...
    cd taskpane
    call npm install
    cd ..
)
cd taskpane
call npm run build
if errorlevel 1 (
    echo ERROR: Task Pane build failed.
    exit /b 1
)
cd ..
echo   Task Pane built to taskpane\dist\

REM ── [3/5] Install Python deps ──────────────────────────────────────────────
echo [3/5] Installing Python dependencies...
cd server
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

REM ── [4/5] Run PyInstaller ─────────────────────────────────────────────────
echo [4/5] Running PyInstaller...
pyinstaller --onedir ^
  --name server ^
  --distpath ..\dist ^
  --workpath ..\build ^
  --add-data "tessdata;tessdata" ^
  --add-data "poppler;poppler" ^
  --add-data "tesseract;tesseract" ^
  --add-data "..\taskpane\dist;taskpane" ^
  --hidden-import uvicorn.logging ^
  --hidden-import uvicorn.loops ^
  --hidden-import uvicorn.loops.auto ^
  --hidden-import uvicorn.protocols ^
  --hidden-import uvicorn.protocols.http ^
  --hidden-import uvicorn.protocols.http.auto ^
  --hidden-import uvicorn.protocols.websockets ^
  --hidden-import uvicorn.protocols.websockets.auto ^
  --hidden-import uvicorn.lifespan ^
  --hidden-import uvicorn.lifespan.on ^
  --hidden-import easyocr ^
  --hidden-import camelot ^
  --hidden-import PIL ^
  --hidden-import cv2 ^
  --collect-all easyocr ^
  --collect-all pytesseract ^
  main.py
if errorlevel 1 (
    echo ERROR: PyInstaller failed.
    cd ..
    exit /b 1
)
cd ..

REM ── [5/5] Verify output ────────────────────────────────────────────────────
echo [5/5] Verifying output...
if not exist "dist\server\server.exe" (
    echo ERROR: dist\server\server.exe not found after build.
    exit /b 1
)
echo.
echo ============================================================
echo  Build complete!
echo    Server bundle : dist\server\
echo    Task Pane dist: taskpane\dist\  (also embedded in bundle)
echo.
echo  Next step: open installer\build.iss in Inno Setup Compiler
echo  or run:   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\build.iss
echo ============================================================
pause
