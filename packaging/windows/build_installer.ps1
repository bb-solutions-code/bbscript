# Requires: Python 3.10+, optional Inno Setup 6 (ISCC.exe) for the Setup.exe step.
param(
    [string] $Version = "0.2.0"
)
$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $repoRoot

Write-Host "Building PyInstaller bundle..." -ForegroundColor Cyan
python (Join-Path $repoRoot "packaging\scripts\build_release.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) {
    $iscc = "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
}
if (-not (Test-Path $iscc)) {
    Write-Host "Inno Setup 6 not found (expected ISCC.exe). Skipping Setup.exe. PyInstaller output: packaging\pyinstaller\dist\bbscript-bundle" -ForegroundColor Yellow
    exit 0
}

$iss = Join-Path $PSScriptRoot "BBScript.iss"
Write-Host "Compiling $iss with version $Version" -ForegroundColor Cyan
& $iscc "/DMyAppVersion=$Version" $iss
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Installer: packaging\windows\dist\BBScript-$Version-Setup.exe" -ForegroundColor Green
