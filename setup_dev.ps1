#Requires -Version 5.1
<#
  Create .venv in this repo, install bbscript and bbpm in editable mode.
  Default: include dev extras. Use -NoDev to skip pytest/ruff/black (bbscript) and dev deps (bbpm).
#>
[CmdletBinding()]
param(
    [switch] $NoDev
)

$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
$Venv = Join-Path $Root ".venv"
$VenvPython = Join-Path $Venv "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Host "Creating venv at $Venv"
    & python -m venv $Venv
}

function Invoke-Pip {
    param([string[]] $PipArgs)
    & $VenvPython -m pip @PipArgs
}

Write-Host "Upgrading pip..."
Invoke-Pip @("install", "--upgrade", "pip")

$bbscriptSpec = if ($NoDev) { $Root } else { $Root + '[dev]' }
Write-Host "Installing bbscript (editable)..."
Invoke-Pip @("install", "-e", $bbscriptSpec)

$nested = Join-Path $Root "bbpm"
$parentBbpm = Join-Path (Split-Path -Parent $Root) "bbpm"
$bbpmPath = $null
if (Test-Path -LiteralPath (Join-Path $nested "pyproject.toml")) {
    $bbpmPath = $nested
}
elseif (Test-Path -LiteralPath (Join-Path $parentBbpm "pyproject.toml")) {
    $bbpmPath = $parentBbpm
}

if ($bbpmPath) {
    $bbpmSpec = if ($NoDev) { $bbpmPath } else { $bbpmPath + '[dev]' }
    Write-Host "Installing local bbpm from $bbpmPath (editable)..."
    Invoke-Pip @("install", "-e", $bbpmSpec)
}
else {
    Write-Warning "No local bbpm checkout found at $($Root)\bbpm or $(Split-Path -Parent $Root)\bbpm. Installing bbpm from PyPI."
    Invoke-Pip @("install", "bbpm")
}

Write-Host ""
Write-Host "Done. Activate the environment:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "Then run: bbscript --help   and   bbpm --help"
