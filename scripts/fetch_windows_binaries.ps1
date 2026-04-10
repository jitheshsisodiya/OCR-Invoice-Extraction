# fetch_windows_binaries.ps1
# Downloads Tesseract and Poppler Windows portable binaries into server\tesseract\ and server\poppler\.
# Run this once on Windows before running installer\build_server.bat.
#
# Tesseract strategy (in order):
#   1. Try NSIS silent install to server\tesseract\
#   2. If that fails, copy from default C:\Program Files\Tesseract-OCR\ (if already installed)
#   3. If that fails, extract from NSIS installer using 7-Zip (if 7z.exe is present)
#   4. If all fail, print clear manual instructions
#
# Poppler: GitHub release ZIP (oschwartz10612)

param(
    [string]$RepoRoot = (Split-Path $PSScriptRoot -Parent)
)

$ErrorActionPreference = "Continue"   # don't abort on non-fatal errors

$TesseractDir = Join-Path $RepoRoot "server\tesseract"
$PopplerDir   = Join-Path $RepoRoot "server\poppler"
$TempDir      = Join-Path $env:TEMP "ocr_binaries"

New-Item -ItemType Directory -Force -Path $TesseractDir | Out-Null
New-Item -ItemType Directory -Force -Path $PopplerDir   | Out-Null
New-Item -ItemType Directory -Force -Path $TempDir      | Out-Null

# ─── Tesseract ────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== Tesseract ===" -ForegroundColor Cyan

$TessExePath = Join-Path $TesseractDir "tesseract.exe"

if (Test-Path $TessExePath) {
    Write-Host "  Already present at $TesseractDir — skipping." -ForegroundColor Green
} else {
    $TessInstaller = Join-Path $TempDir "tesseract-setup.exe"
    $TessUrl = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.4.20231005.exe"

    # ── Step 1: Download installer ──────────────────────────────────────────────
    if (-not (Test-Path $TessInstaller)) {
        Write-Host "  Downloading UB-Mannheim Tesseract 5.3.4 installer..."
        try {
            Invoke-WebRequest -Uri $TessUrl -OutFile $TessInstaller -UseBasicParsing
            Write-Host "  Download complete." -ForegroundColor Green
        } catch {
            Write-Warning "  Download failed: $_"
            $TessInstaller = $null
        }
    } else {
        Write-Host "  Installer already in temp folder, reusing."
    }

    # ── Step 2: NSIS silent install to custom path ──────────────────────────────
    if ($TessInstaller -and (Test-Path $TessInstaller)) {
        Write-Host "  Trying silent install to: $TesseractDir"
        try {
            $proc = Start-Process -FilePath $TessInstaller `
                -ArgumentList "/S /D=$TesseractDir" `
                -Wait -PassThru -NoNewWindow
            Start-Sleep -Seconds 3   # NSIS may still be finalising
        } catch {
            Write-Warning "  Silent install process error: $_"
        }
    }

    # ── Step 3: Fallback — copy from default Program Files install ───────────────
    if (-not (Test-Path $TessExePath)) {
        $DefaultDirs = @(
            "C:\Program Files\Tesseract-OCR",
            "C:\Program Files (x86)\Tesseract-OCR"
        )
        foreach ($dir in $DefaultDirs) {
            if (Test-Path (Join-Path $dir "tesseract.exe")) {
                Write-Host "  Found Tesseract at '$dir' — copying to $TesseractDir ..."
                robocopy "$dir" "$TesseractDir" /E /NP /NFL /NDL 2>&1 | Out-Null
                Write-Host "  Copy done." -ForegroundColor Green
                break
            }
        }
    }

    # ── Step 4: Fallback — 7-Zip extraction from NSIS installer ─────────────────
    if (-not (Test-Path $TessExePath)) {
        $SevenZipPaths = @(
            "C:\Program Files\7-Zip\7z.exe",
            "C:\Program Files (x86)\7-Zip\7z.exe"
        )
        $SevenZip = $SevenZipPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

        if ($SevenZip -and $TessInstaller -and (Test-Path $TessInstaller)) {
            Write-Host "  Trying 7-Zip extraction of NSIS installer..."
            $ExtractPath = Join-Path $TempDir "tess_7z_extract"
            New-Item -ItemType Directory -Force -Path $ExtractPath | Out-Null
            & $SevenZip x $TessInstaller "-o$ExtractPath" -y 2>&1 | Out-Null

            # NSIS extracts app files into $INSTDIR; find tesseract.exe
            $FoundExe = Get-ChildItem -Path $ExtractPath -Recurse -Filter "tesseract.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($FoundExe) {
                $SourceDir = $FoundExe.Directory.FullName
                Write-Host "  Copying from extracted dir: $SourceDir"
                Copy-Item -Path "$SourceDir\*" -Destination $TesseractDir -Recurse -Force
                Write-Host "  7-Zip extraction succeeded." -ForegroundColor Green
            } else {
                Write-Warning "  tesseract.exe not found in 7-Zip extraction."
            }
        } elseif (-not $SevenZip) {
            Write-Host "  7-Zip not found; skipping extraction fallback."
        }
    }

    # ── Final status ─────────────────────────────────────────────────────────────
    if (Test-Path $TessExePath) {
        Write-Host "  Tesseract ready: $TessExePath" -ForegroundColor Green
    } else {
        Write-Warning "  TESSERACT NOT INSTALLED. Manual steps:"
        Write-Host ""
        Write-Host "  Option A — Run installer with GUI:"
        Write-Host "    1. Double-click: $TessInstaller"
        Write-Host "    2. When asked for install path, enter EXACTLY:"
        Write-Host "       $TesseractDir"
        Write-Host ""
        Write-Host "  Option B — Copy from existing install (if Tesseract is already on the PC):"
        Write-Host "    Run in CMD (as any user):"
        Write-Host "    robocopy `"C:\Program Files\Tesseract-OCR`" `"$TesseractDir`" /E"
        Write-Host ""
        Write-Host "  Option C — Install via winget, then copy:"
        Write-Host "    winget install UB-Mannheim.TesseractOCR"
        Write-Host "    robocopy `"C:\Program Files\Tesseract-OCR`" `"$TesseractDir`" /E"
        Write-Host ""
    }
}

# ─── Poppler ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== Poppler ===" -ForegroundColor Cyan

$PopplerExe = Join-Path $PopplerDir "bin\pdftoppm.exe"

if (Test-Path $PopplerExe) {
    Write-Host "  Already present at $PopplerDir — skipping." -ForegroundColor Green
} else {
    $PopplerZip = Join-Path $TempDir "poppler-windows.zip"
    $PopplerReleaseApi = "https://api.github.com/repos/oschwartz10612/poppler-windows/releases/latest"

    try {
        Write-Host "  Fetching latest Poppler release info..."
        $Release = Invoke-RestMethod -Uri $PopplerReleaseApi -UseBasicParsing
        $Asset   = $Release.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
        if (-not $Asset) { throw "No zip asset in release." }

        Write-Host "  Downloading $($Asset.name)..."
        Invoke-WebRequest -Uri $Asset.browser_download_url -OutFile $PopplerZip -UseBasicParsing

        $ExtractPath = Join-Path $TempDir "poppler_extract"
        Remove-Item -Path $ExtractPath -Recurse -Force -ErrorAction SilentlyContinue
        Expand-Archive -Path $PopplerZip -DestinationPath $ExtractPath -Force

        # Find bin/ directory inside extracted archive
        $BinDir = Get-ChildItem -Path $ExtractPath -Recurse -Directory -Filter "bin" | Select-Object -First 1
        if ($BinDir) {
            # Copy the parent of bin/ (which contains bin/ and lib/) to PopplerDir
            $SourceRoot = $BinDir.Parent.FullName
            Copy-Item -Path "$SourceRoot\*" -Destination $PopplerDir -Recurse -Force
            Write-Host "  Poppler ready: $PopplerExe" -ForegroundColor Green
        } else {
            Write-Warning "  Could not locate bin/ inside Poppler zip."
        }
    } catch {
        Write-Warning "  Poppler auto-download failed: $_"
        Write-Host "  Manual step: Download from https://github.com/oschwartz10612/poppler-windows/releases"
        Write-Host "  Extract so that pdftoppm.exe is at: $PopplerExe"
    }
}

# ─── Summary ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host " Binary setup complete." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$TessOk   = Test-Path (Join-Path $TesseractDir "tesseract.exe")
$PopplerOk = Test-Path (Join-Path $PopplerDir "bin\pdftoppm.exe")

Write-Host ("  Tesseract : " + $(if ($TessOk)    { "[OK] $TesseractDir" } else { "[MISSING] $TesseractDir" }))
Write-Host ("  Poppler   : " + $(if ($PopplerOk) { "[OK] $PopplerDir"   } else { "[MISSING] $PopplerDir" }))
Write-Host ""

if ($TessOk -and $PopplerOk) {
    Write-Host "  All binaries present. Run next:" -ForegroundColor Green
    Write-Host "    installer\build_server.bat"
} else {
    Write-Warning "  One or more binaries missing — fix them before running build_server.bat"
}
