; Inno Setup Script for Norwegian Dictionary Lookup
; This creates a professional installer for the application

#define MyAppName "Norwegian Dictionary Lookup"
#define MyAppVersion "1.0"
#define MyAppPublisher "Ethan Hamilton"
#define MyAppExeName "NorwegianDictionary.exe"

[Setup]
; Basic app info
AppId={{3E443C3C-DE85-423F-8C82-7968937BB0D2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
; Don't create program group (no Start Menu shortcuts)
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=NorwegianDictionary_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Uninstall
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "startup"; Description: "Start automatically when Windows starts (Recommended)"; GroupDescription: "Startup Options:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; No shortcuts created - program runs in background only

[Registry]
; Add to startup if user selected the option
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "NorwegianDictionary"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletevalue; Tasks: startup

[Run]
; Run the application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('Installation Complete!' + #13#10 + #13#10 +
           'QUICK START:' + #13#10 +
           '1. The program will start automatically in a moment' + #13#10 +
           '2. Try it: Select a Norwegian word' + #13#10 +
           '3. Press Alt+P+N to see the translation' + #13#10 + #13#10 +
           'The program runs in the background - you won''t see a window.' + #13#10 +
           'It''s ready whenever you need it!',
           mbInformation, MB_OK);
  end;
end;