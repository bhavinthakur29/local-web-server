# Zip dist\TekServeLocal for GitHub Releases (README download button).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$src = Join-Path $PSScriptRoot "dist\TekServeLocal"
$zip = Join-Path $PSScriptRoot "TekServeLocal-Windows.zip"

if (-not (Test-Path (Join-Path $src "TekServeLocal.exe"))) {
    throw "Run .\build.ps1 first. dist\TekServeLocal\TekServeLocal.exe not found."
}

if (Test-Path $zip) {
    Remove-Item $zip -Force
}

Compress-Archive -Path $src -DestinationPath $zip -Force

Write-Host "Release package ready:"
Write-Host "  $zip"
Write-Host ""
Write-Host "Upload to GitHub:"
Write-Host '  gh release create v1.0.0 TekServeLocal-Windows.zip --title v1.0.0'
