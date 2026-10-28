; Development-only unsigned installer. It is not a stable release.
#define AppName "DOTX Browser (Development)"
#define AppExeName "DOTX.exe"
[Setup]
AppId={{FC49EE83-E32A-4D88-AE6E-CA21637A8197}
AppName={#AppName}
AppVersion=0.0.0-dev
AppVerName=DOTX Browser (Development)
AppPublisher=dotsoftwarelk
VersionInfoVersion=0.0.0.0
DefaultDirName={localappdata}\Programs\DOTX Development
DefaultGroupName=DOTX Browser Development
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\artifacts
OutputBaseFilename=DOTX-development-setup-x64-unsigned
Compression=lzma2
SolidCompression=yes
UninstallDisplayIcon={app}\{#AppExeName}
WizardStyle=modern
[Files]
Source: "..\dist\DOTX\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\DOTX Browser (Development)"; Filename: "{app}\{#AppExeName}"
[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch DOTX Browser (Development)"; Flags: nowait postinstall skipifsilent
