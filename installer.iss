#define AppName "AEMULUS"
#define AppVersion "0.2.0-beta"
[Setup]
AppId={{A7B86D60-0A9E-4F2D-B6C5-4EAB3E6E89D1}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\AEMULUS
DefaultGroupName=AEMULUS
OutputDir=output
OutputBaseFilename=AEMULUS-Setup-x64
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
WizardStyle=modern
UninstallDisplayIcon={app}\AEMULUS.exe
[Files]
Source: "dist\AEMULUS\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
[Icons]
Name: "{group}\AEMULUS"; Filename: "{app}\AEMULUS.exe"
Name: "{autodesktop}\AEMULUS"; Filename: "{app}\AEMULUS.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Utworz skrot na pulpicie"; Flags: unchecked
[Run]
Filename: "{app}\AEMULUS.exe"; Description: "Uruchom AEMULUS"; Flags: nowait postinstall skipifsilent
