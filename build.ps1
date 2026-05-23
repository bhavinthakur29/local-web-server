# Build TekServe Local for Windows (folder-based app, fewer AV false positives than onefile).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Installing build dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt

# Obsolete stdlib backports break PyInstaller on Python 3.13+
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
foreach ($pkg in @("typing", "pathlib", "enum34", "ipaddress")) {
    python -m pip uninstall -y $pkg *>$null
}
$ErrorActionPreference = $prevEAP

Write-Host "Building TekServe Local..."
python -m PyInstaller tekserve_local.spec --noconfirm --clean

$out = Join-Path $PSScriptRoot "dist\TekServeLocal"
if (-not (Test-Path (Join-Path $out "TekServeLocal.exe"))) {
    throw "Build failed: TekServeLocal.exe not found in dist\TekServeLocal"
}

Write-Host ""
Write-Host "Build complete:"
Write-Host "  $out\TekServeLocal.exe"
Write-Host ""
Write-Host "Distribute the entire TekServeLocal folder (not only the .exe)."
Write-Host "For fewer SmartScreen warnings, sign the executable with an Authenticode certificate."
Write-Host "See README.md section 'Building the Windows app'."
