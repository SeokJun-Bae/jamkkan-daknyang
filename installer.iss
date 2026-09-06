#ifndef MyAppVersion
  #define MyAppVersion "0.1.1"
#endif

#define MyAppName "잠깐닦냥"
#define MyAppExeName "잠깐닦냥.exe"
#define MySourceExeName "JamkkanDaknyang.exe"

[Setup]
AppId={{6D143B8B-B802-4D78-A2C8-E64D88078B5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=SeokJun-Bae
AppPublisherURL=https://github.com/SeokJun-Bae/jamkkan-daknyang
AppSupportURL=https://github.com/SeokJun-Bae/jamkkan-daknyang/issues
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=JamkkanDaknyang-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupLogging=yes
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MySourceExeName}"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

