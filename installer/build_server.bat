@echo off
REM ============================================================
REM Build the OCR Invoice Extraction server bundle.
REM Run from the REPO ROOT on Windows.
REM
REM Pre-requisites:
REM   server\tessdata\  - eng.traineddata (already in repo)
REM   server\tesseract\ - tesseract.exe + DLLs
REM   server\poppler\   - bin\pdftoppm.exe etc.
REM     -> Run once: powershell scripts\fetch_windows_binaries.ps1
REM
REM Output:
REM   dist\server\server.exe   (used by Inno Setup build.iss)
REM ============================================================
setlocal

echo ============================================================
echo  OCR Invoice Extraction - Server Build
echo ============================================================

REM ── [1/5] Verify required binaries ───────────────────────────
echo [1/5] Verifying required binaries...
if not exist "server\tessdata\eng.traineddata" (
    echo ERROR: server\tessdata\eng.traineddata not found.
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

REM ── [2/5] Build task pane ─────────────────────────────────────
echo [2/5] Building Task Pane (npm run build)...
if not exist "taskpane\node_modules" (
    cd taskpane && call npm install && cd ..
)
cd taskpane
call npm run build
if errorlevel 1 ( echo ERROR: npm build failed. & exit /b 1 )
cd ..
echo   OK: taskpane\dist\

REM ── [3/5] Install Python deps ─────────────────────────────────
echo [3/5] Installing Python dependencies...
cd server
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
cd ..

REM ── [4/5] PyInstaller via spec file ───────────────────────────
echo [4/5] Running PyInstaller (installer\server.spec)...
pyinstaller installer\server.spec --noconfirm
if errorlevel 1 ( echo ERROR: PyInstaller failed. & exit /b 1 )

REM ── [5/5] Verify output ───────────────────────────────────────
echo [5/5] Verifying output...
if not exist "dist\server\server.exe" (
    echo ERROR: dist\server\server.exe not found.
    exit /b 1
)
echo.
echo ============================================================
echo  Build complete!
echo    Server bundle: dist\server\
echo.
echo  Next: compile the installer
echo    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\build.iss
echo    Output: installer\Output\OCRInvoiceExtraction_Setup.exe
echo ============================================================
pause
