# trust_manifest.ps1
# Sideloads the OCR Invoice Extraction manifest into Excel for development.
# Run as Administrator or current user (user-level trusted catalog).

$manifestDir = Resolve-Path "$PSScriptRoot\..\taskpane"
$catalogGuid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
$registryBase = "HKCU:\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\$catalogGuid"

Write-Host "Registering manifest directory as trusted catalog..." -ForegroundColor Cyan
Write-Host "  Path: $manifestDir"

New-Item -Path $registryBase -Force | Out-Null
Set-ItemProperty -Path $registryBase -Name "Id" -Value "{$catalogGuid}"
Set-ItemProperty -Path $registryBase -Name "Url" -Value $manifestDir.Path
Set-ItemProperty -Path $registryBase -Name "Flags" -Value 1

Write-Host "Done! To load the add-in:" -ForegroundColor Green
Write-Host "  1. Open Excel"
Write-Host "  2. Insert > My Add-ins > Shared Folder"
Write-Host "  3. Select 'OCR Invoice Extraction'"
Write-Host ""
Write-Host "Make sure the dev server is running: scripts\dev_start.bat"
