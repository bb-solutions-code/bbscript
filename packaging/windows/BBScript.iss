; Build after: python packaging/scripts/build_release.py
; Output: dist/BBScript-{version}-Setup.exe (run Inno Setup Compiler)

#define MyAppName "BBScript"
#define MyAppPublisher "BBScript"
#define MyAppExeName "bbscript.exe"
#define BundleDir "..\\pyinstaller\\dist\\bbscript-bundle"

#ifndef MyAppVersion
#define MyAppVersion "0.2.0"
#endif

[Setup]
AppId={{A8B9C0D1-E2F3-4455-6677-8899AABBCCDD}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\BBScript
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=BBScript-{#MyAppVersion}-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#BundleDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}\bbscript"; Filename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName}\bbpm"; Filename: "{app}\bbpm.exe"

[Code]
function NeedsAddPath(Dir: string): Boolean;
var
  Path: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', Path) then
    Result := True
  else
    Result := Pos(';' + LowerCase(Dir) + ';', ';' + LowerCase(Path) + ';') = 0;
end;

procedure AddToUserPath(const Dir: string);
var
  Path: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', Path) then
    Path := '';
  if Path <> '' then Path := Path + ';';
  Path := Path + Dir;
  if RegWriteExpandStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', Path) then
    Log('Updated user PATH');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if NeedsAddPath(ExpandConstant('{app}')) then
      AddToUserPath(ExpandConstant('{app}'));
  end;
end;

