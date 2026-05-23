# Create and push a version tag so GitHub Actions publishes release downloads.
param(
    [string]$Version = "v1.0.0"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if ($Version -notmatch "^v") {
    $Version = "v$Version"
}

Write-Host "This will create tag $Version and push it to origin."
Write-Host "GitHub Actions will build Windows, Linux, and macOS installers."
Write-Host "Watch: https://github.com/bhavinthakur29/local-web-server/actions"
Write-Host ""

$existing = git tag -l $Version
if ($existing) {
    Write-Host "Tag $Version already exists locally."
    $reply = Read-Host "Push it to origin anyway? (y/N)"
    if ($reply -ne "y") { exit 0 }
} else {
    git tag $Version
    Write-Host "Created tag $Version"
}

git push origin $Version

Write-Host ""
Write-Host "Pushed $Version. When Actions finishes, downloads will be at:"
Write-Host "  https://github.com/bhavinthakur29/local-web-server/releases/latest"
