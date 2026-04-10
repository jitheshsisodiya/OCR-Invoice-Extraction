; Inno Setup Script for OCR Invoice Extraction Excel Add-in
; Run with Inno Setup Compiler to produce setup.exe
;
; Pre-requisites (run from repo root on Windows):
;   installer\build_server.bat    -> dist\server\   (PyInstaller output)
;   installer\build_taskpane.bat  -> taskpane\dist\

#define MyAppName "OCR Invoice Extraction"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "OCR Invoice Extraction"
#define MyAppURL "http://localhost:7432"
#define MyAppExeName "server\server.exe"
#define AddinGUID "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\OCRInvoiceExtraction
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=OCRInvoiceExtraction_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64 arm64
MinVersion=10.0
; Installer visuals
WizardImageFile=assets\installer_banner.bmp
WizardSmallImageFile=assets\installer_small.bmp
SetupIconFile=assets\installer_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "startupentry"; Description: "Start OCR server automatically at Windows login"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
; Python server bundle (PyInstaller --onedir output).
; The taskpane dist is already bundled inside _internal\taskpane\ by server.spec,
; so no separate taskpane copy is needed here.
Source: "..\dist\server\*"; DestDir: "{app}\server"; Flags: ignoreversion recursesubdirs createallsubdirs

; Production manifest (references localhost:7432, not localhost:3000)
Source: "..\taskpane\manifest.prod.xml"; DestDir: "{app}"; DestName: "manifest.xml"; Flags: ignoreversion

; Default .env — only written if it doesn't already exist (preserves user's API key)
Source: "..\server\.env.example"; DestDir: "{app}"; DestName: ".env"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName}";          Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Registry]
; Register the manifest directory as a trusted catalog for Excel add-ins
; Excel reads manifests from any directory listed under TrustedCatalogs.
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{{{#AddinGUID}}"; ValueType: string; ValueName: "Id";    ValueData: "{{{#AddinGUID}}}"
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{{{#AddinGUID}}"; ValueType: string; ValueName: "Url";   ValueData: "{app}"
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{{{#AddinGUID}}"; ValueType: dword;  ValueName: "Flags"; ValueData: "1"

; Auto-start server on Windows login (optional task)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "OCRInvoiceServer"; \
  ValueData: """{app}\{#MyAppExeName}"""; Tasks: startupentry

[Run]
; Launch server immediately after install (hidden, no console window)
Filename: "{app}\{#MyAppExeName}"; Description: "Start OCR server now"; Flags: nowait runhidden postinstall

[UninstallRun]
; Kill the server process on uninstall
Filename: "taskkill"; Parameters: "/F /IM server.exe"; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{app}\data"
Type: files;          Name: "{app}\ocr_invoice.db"

[Code]
// ---------------------------------------------------------------------------
// After install: confirm the manifest was registered and show load instructions
// ---------------------------------------------------------------------------
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    MsgBox(
      'Installation complete!' + #13#10 + #13#10 +
      'To load the add-in in Excel:' + #13#10 +
      '  1. Open Excel' + #13#10 +
      '  2. File > Options > Trust Center > Trust Center Settings' + #13#10 +
      '     > Trusted Add-in Catalogs' + #13#10 +
      '  3. The catalog path "' + ExpandConstant('{app}') + '" should' + #13#10 +
      '     already appear. If not, add it manually and tick "Show in Menu".' + #13#10 +
      '  4. Insert > My Add-ins > Shared Folder > OCR Invoice Extraction' + #13#10 + #13#10 +
      'The OCR server (localhost:7432) starts automatically in the background.' + #13#10 + #13#10 +
      'Optional: edit ' + ExpandConstant('{app}') + '\.env to add your' + #13#10 +
      'ANTHROPIC_API_KEY for AI-powered Form Extraction and Summarization.',
      mbInformation, MB_OK);
  end;
end;
