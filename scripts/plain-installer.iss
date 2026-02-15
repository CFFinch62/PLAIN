; PLAIN Installer Script for Inno Setup
; Requires Inno Setup 6.0 or later: https://jrsoftware.org/isinfo.php

#define MyAppName "PLAIN"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Fragillidae Software"
#define MyAppURL "https://github.com/CFFinch62/plain-language"
#define MyAppExeName "plain-ide.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{8F9A3B2C-1D4E-5F6A-7B8C-9D0E1F2A3B4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\releases
OutputBaseFilename=PLAIN-Setup-v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
SetupIconFile=..\images\plain_icon_256.png
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "addtopath"; Description: "Add PLAIN interpreter to PATH"; GroupDescription: "System Integration:"; Flags: unchecked
Name: "fileassoc"; Description: "Associate .plain files with PLAIN IDE"; GroupDescription: "System Integration:"

[Files]
; Interpreter
Source: "..\plain.exe"; DestDir: "{app}"; Flags: ignoreversion

; IDE
Source: "..\dist\plain-ide\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\INSTALLATION.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs

; Examples
Source: "..\examples\*"; DestDir: "{app}\examples"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\PLAIN IDE"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\PLAIN Interpreter (Command Line)"; Filename: "cmd.exe"; Parameters: "/K ""{app}\plain.exe"""; WorkingDir: "{app}"
Name: "{group}\Documentation"; Filename: "{app}\docs"
Name: "{group}\Examples"; Filename: "{app}\examples"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop icon (optional)
Name: "{autodesktop}\{#MyAppName} IDE"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Registry]
; File association for .plain files
Root: HKA; Subkey: "Software\Classes\.plain"; ValueType: string; ValueName: ""; ValueData: "PLAINFile"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKA; Subkey: "Software\Classes\PLAINFile"; ValueType: string; ValueName: ""; ValueData: "PLAIN Program"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKA; Subkey: "Software\Classes\PLAINFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: fileassoc
Root: HKA; Subkey: "Software\Classes\PLAINFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: fileassoc

[Code]
const
  EnvironmentKey = 'Environment';

procedure CurStepChanged(CurStep: TSetupStep);
var
  Path: string;
  AppPath: string;
begin
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('addtopath') then
  begin
    AppPath := ExpandConstant('{app}');
    
    // Get current PATH
    if RegQueryStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', Path) then
    begin
      // Check if already in PATH
      if Pos(';' + Uppercase(AppPath) + ';', ';' + Uppercase(Path) + ';') = 0 then
      begin
        // Add to PATH
        Path := Path + ';' + AppPath;
        RegWriteStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', Path);
      end;
    end
    else
    begin
      // PATH doesn't exist, create it
      RegWriteStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', AppPath);
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Path: string;
  AppPath: string;
  P: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    AppPath := ExpandConstant('{app}');
    
    if RegQueryStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', Path) then
    begin
      // Remove from PATH
      P := Pos(';' + Uppercase(AppPath) + ';', ';' + Uppercase(Path) + ';');
      if P > 0 then
      begin
        Delete(Path, P, Length(AppPath) + 1);
        RegWriteStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', Path);
      end;
    end;
  end;
end;

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

