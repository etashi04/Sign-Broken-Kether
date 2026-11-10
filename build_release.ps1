param([string]$Python="python")
$ErrorActionPreference="Stop"
& $Python (Join-Path $PSScriptRoot "build_release.py")
if ($LASTEXITCODE -ne 0) { throw "Release build failed" }
