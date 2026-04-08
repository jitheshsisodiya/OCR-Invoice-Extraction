@echo off
REM Build the Python FastAPI server into a standalone .exe using PyInstaller
REM Run this from the repo root on Windows.

echo [1/3] Installing dependencies...
cd server
pip install -r requirements.txt
pip install pyinstaller

echo [2/3] Running PyInstaller...
pyinstaller --onefile ^
  --name server ^
  --add-data "tessdata;tessdata" ^
  --add-data "poppler;poppler" ^
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
  main.py

echo [3/3] Output: server\dist\server.exe
cd ..
pause
