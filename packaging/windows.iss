[Setup]
AppId=BibleSmartDisplay
AppName=Bible Smart Display
AppVersion=0.4.0
DefaultDirName={localappdata}\Programs\BibleSmartDisplay
DefaultGroupName=Bible Smart Display
PrivilegesRequired=lowest
OutputDir=artifacts
OutputBaseFilename=bibleSmartDisplay-windows-x64-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\BibleSmartDisplay.exe
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
[Files]
Source: "..\dist\BibleSmartDisplay\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Bible Smart Display"; Filename: "{app}\BibleSmartDisplay.exe"
[Run]
Filename: "{app}\BibleSmartDisplay.exe"; Description: "Open Bible Smart Display"; Flags: nowait postinstall skipifsilent
[UninstallRun]
Filename: "{app}\BibleSmartDisplay.exe"; Parameters: "--remove-setup"; Flags: runhidden waituntilterminated
