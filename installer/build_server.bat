@echo off
REM ============================================================
REM Build the Python FastAPI server into a standalone .exe
REM using PyInstaller.  Run this script from the repo root on
REM Windows after placing the required binaries (see below).
REM
REM Required before running:
REM   server\tessdata\       - eng.traineddata, osd.traineddata
REM                            (already present in repo)
REM   server\poppler\bin\    - pdftoppm.exe, pdfinfo.exe, etc.
REM                            Download from:
REM                            https://github.com/oschwartz10612/poppler-windows/releases
REM   server\tesseract\      - tesseract.exe + all DLLs
REM                            Download portable build from:
REM                            https://github.com/UB-Mannheim/tesseract/wiki
REM ============================================================

echo [1/4] Verifying required binaries...
if not exist "server\tessdata\eng.traineddata" (
    echo ERROR: server\tessdata\eng.traineddata not found.
    exit /b 1
)
if not exist "server\poppler\bin\pdftoppm.exe" (
    echo ERROR: server\poppler\bin\pdftoppm.exe not found.
    echo        Download Poppler for Windows: https://github.com/oschwartz10612/poppler-windows/releases
    exit /b 1
)
if not exist "server\tesseract\tesseract.exe" (
    echo ERROR: server\tesseract\tesseract.exe not found.
    echo        Download: https://github.com/UB-Mannheim/tesseract/wiki
    exit /b 1
)

echo [2/4] Installing Python dependencies...
cd server
pip install -r requirements.txt
pip install pyinstaller

echo [3/4] Running PyInstaller...
pyinstaller --onedir ^
  --name server ^
  --distpath ..\dist ^
  --workpath ..\build ^
  --add-data "tessdata;tessdata" ^
  --add-data "poppler;poppler" ^
  --add-data "tesseract;tesseract" ^
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

echo [4/4] Done. Output: dist\server\server.exe
cd ..
pause
