@echo off
echo Starting OCR Invoice Extraction development environment...

REM Start Python FastAPI server in background
echo [1/2] Starting Python OCR server on port 7432...
start "OCR Server" cmd /k "cd /d %~dp0..\server && python main.py"

REM Wait a moment for server to initialize
timeout /t 2 /nobreak >nul

REM Start Vite dev server for Task Pane
echo [2/2] Starting Task Pane dev server on port 3000...
start "Task Pane Dev" cmd /k "cd /d %~dp0..\taskpane && npm run dev"

echo.
echo Development servers started:
echo   OCR Server:  http://127.0.0.1:7432
echo   Task Pane:   http://localhost:3000
echo   API Docs:    http://127.0.0.1:7432/docs
echo.
echo To sideload the add-in in Excel, run: scripts\trust_manifest.ps1
pause
