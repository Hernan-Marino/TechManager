; ============================================================================
; TECHMANAGER v1.0 - INSTALADOR PROFESIONAL
; Script de Inno Setup
; ============================================================================

#define MyAppName "TechManager"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "TechManager"
#define MyAppURL "https://www.techmanager.com"
#define MyAppExeName "TechManager.exe"

[Setup]
AppId={{A7B3C4D5-E6F7-8901-2345-6789ABCDEF01}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
PrivilegesRequired=admin
OutputDir=instalador
OutputBaseFilename=TechManager_v1.0_Installer
SetupIconFile=recursos\iconos\techmanager.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE.txt
InfoBeforeFile=ANTES_DE_INSTALAR.txt
InfoAfterFile=DESPUES_DE_INSTALAR.txt
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
ShowLanguageDialog=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el Escritorio"; GroupDescription: "Accesos directos:"; Flags: checkablealone

[Files]
Source: "dist\TechManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "datos\*"; DestDir: "{app}\datos"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "recursos\*"; DestDir: "{app}\recursos"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  if Version.Major < 6 then
  begin
    MsgBox('Este programa requiere Windows 7 o superior.', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Crear carpetas necesarias
    CreateDir(ExpandConstant('{app}\logs'));
    CreateDir(ExpandConstant('{app}\datos\backups'));
    CreateDir(ExpandConstant('{app}\datos\exportaciones'));
    CreateDir(ExpandConstant('{app}\datos\temporal'));
    
    // Dar permisos de escritura a carpetas de datos y logs
    // Usando icacls de Windows para dar permisos completos a Users
    Exec('icacls', '"' + ExpandConstant('{app}\datos') + '" /grant Users:(OI)(CI)F /T /C /Q', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec('icacls', '"' + ExpandConstant('{app}\logs') + '" /grant Users:(OI)(CI)F /T /C /Q', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
