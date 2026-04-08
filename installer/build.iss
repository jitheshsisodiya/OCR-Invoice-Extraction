; Inno Setup Script for OCR Invoice Extraction Excel Add-in
; Run with Inno Setup Compiler to produce setup.exe

#define MyAppName "OCR Invoice Extraction"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "OCR Invoice Extraction"
#define MyAppURL "https://localhost:3000"
#define MyAppExeName "server.exe"
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

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "startupentry"; Description: "Start OCR server automatically at Windows login"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
; Python server executable (built by build_server.bat)
Source: "..\server\dist\server.exe"; DestDir: "{app}"; Flags: ignoreversion

; Task Pane web files (built by build_taskpane.bat)
Source: "..\taskpane\dist\*"; DestDir: "{app}\taskpane"; Flags: ignoreversion recursesubdirs createallsubdirs

; Office Add-in manifest
Source: "..\taskpane\manifest.xml"; DestDir: "{app}"; Flags: ignoreversion

; Default .env config
Source: "..\server\.env.example"; DestDir: "{app}"; DestName: ".env"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Registry]
; Register the manifest directory as a trusted catalog for Excel add-ins
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{{{#AddinGUID}}"; ValueType: string; ValueName: "Id"; ValueData: "{{{#AddinGUID}}}"
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{{{#AddinGUID}}"; ValueType: string; ValueName: "Url"; ValueData: "{app}"
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{{{#AddinGUID}}"; ValueType: dword; ValueName: "Flags"; ValueData: "1"

; Auto-start: add server to Windows startup (optional task)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "OCRInvoiceServer"; ValueData: """{app}\server.exe"""; Tasks: startupentry

[Run]
; Start the server immediately after install
Filename: "{app}\server.exe"; Description: "Start OCR server now"; Flags: nowait runhidden postinstall

[UninstallRun]
; Stop server on uninstall
Filename: "taskkill"; Parameters: "/F /IM server.exe"; Flags: runhidden

[UninstallDelete]
; Clean up database and thumbnails
Type: filesandordirs; Name: "{app}\data"
Type: files; Name: "{app}\ocr_invoice.db"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    MsgBox('Installation complete!' + #13#10 + #13#10 +
           'To load the add-in in Excel:' + #13#10 +
           '1. Open Excel' + #13#10 +
           '2. Go to Insert > My Add-ins > Shared Folder' + #13#10 +
           '3. Select "OCR Invoice Extraction"' + #13#10 + #13#10 +
           'The OCR server starts automatically in the background.',
           mbInformation, MB_OK);
  end;
end;
