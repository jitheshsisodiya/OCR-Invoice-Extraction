# fetch_windows_binaries.ps1
# Downloads Tesseract and Poppler Windows portable binaries into server\tesseract\ and server\poppler\.
# Run this once on Windows before running installer\build_server.bat.
#
# Sources:
#   Tesseract: UB-Mannheim portable installer (extracted silently)
#   Poppler:   oschwartz10612 pre-built Windows release

param(
    [string]$RepoRoot = (Split-Path $PSScriptRoot -Parent)
)

$ErrorActionPreference = "Stop"

$TesseractDir = Join-Path $RepoRoot "server\tesseract"
$PopperDir    = Join-Path $RepoRoot "server\poppler"
$TempDir      = Join-Path $env:TEMP "ocr_binaries"

New-Item -ItemType Directory -Force -Path $TesseractDir | Out-Null
New-Item -ItemType Directory -Force -Path $PopperDir    | Out-Null
New-Item -ItemType Directory -Force -Path $TempDir      | Out-Null

# ─── Tesseract ────────────────────────────────────────────────────────────────
Write-Host "Downloading Tesseract 5.x for Windows..." -ForegroundColor Cyan
$TessInstaller = Join-Path $TempDir "tesseract-setup.exe"
# UB-Mannheim latest 5.x x64 installer
$TessUrl = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.4.20231005.exe"

try {
    Invoke-WebRequest -Uri $TessUrl -OutFile $TessInstaller -UseBasicParsing
    Write-Host "Installing Tesseract silently to $TesseractDir..."
    Start-Process -FilePath $TessInstaller -ArgumentList "/S /D=$TesseractDir" -Wait
    Write-Host "Tesseract installed." -ForegroundColor Green
} catch {
    Write-Warning "Auto-download failed: $_"
    Write-Host "Manual step: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    Write-Host "             and extract to: $TesseractDir"
}

# ─── Poppler ──────────────────────────────────────────────────────────────────
Write-Host "Downloading Poppler for Windows..." -ForegroundColor Cyan
$PopperZip = Join-Path $TempDir "poppler-windows.zip"
# Latest release from oschwartz10612
$PopperReleaseApi = "https://api.github.com/repos/oschwartz10612/poppler-windows/releases/latest"

try {
    $Release = Invoke-RestMethod -Uri $PopperReleaseApi -UseBasicParsing
    $Asset   = $Release.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
    $PopperUrl = $Asset.browser_download_url
    Write-Host "  Downloading $($Asset.name)..."
    Invoke-WebRequest -Uri $PopperUrl -OutFile $PopperZip -UseBasicParsing

    # Extract
    $ExtractPath = Join-Path $TempDir "poppler_extract"
    Expand-Archive -Path $PopperZip -DestinationPath $ExtractPath -Force

    # Find the bin/ folder inside the extracted zip
    $BinFolder = Get-ChildItem -Path $ExtractPath -Recurse -Directory -Filter "bin" | Select-Object -First 1
    if ($BinFolder) {
        Copy-Item -Path $BinFolder.FullName -Destination $PopperDir -Recurse -Force
        Write-Host "Poppler installed." -ForegroundColor Green
    } else {
        # Some releases have Library/bin structure
        $LibBin = Get-ChildItem -Path $ExtractPath -Recurse -Directory | Where-Object { $_.Name -eq "bin" } | Select-Object -First 1
        if ($LibBin) {
            Copy-Item -Path $LibBin.FullName -Destination $PopperDir -Recurse -Force
            Write-Host "Poppler installed." -ForegroundColor Green
        } else {
            Write-Warning "Could not find bin/ folder in Poppler zip."
        }
    }
} catch {
    Write-Warning "Auto-download failed: $_"
    Write-Host "Manual step: Download from https://github.com/oschwartz10612/poppler-windows/releases"
    Write-Host "             and extract the 'bin' folder to: $PopperDir\bin"
}

# ─── Summary ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Binary setup complete." -ForegroundColor Green
Write-Host "  Tesseract: $TesseractDir"
Write-Host "  Poppler:   $PopperDir"
Write-Host ""
Write-Host "Next: run installer\build_server.bat"
