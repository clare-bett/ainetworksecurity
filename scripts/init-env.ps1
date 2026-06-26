$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$EnvFile = Join-Path $RootDir ".env"

if (Test-Path $EnvFile) {
    Write-Host ".env already exists: $EnvFile"
    exit 0
}

$Bytes = New-Object byte[] 32
$Rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try {
    $Rng.GetBytes($Bytes)
}
finally {
    $Rng.Dispose()
}
$Seed = -join ($Bytes | ForEach-Object { $_.ToString("x2") })

Set-Content -Path $EnvFile -Value "FLAG_SEED=$Seed" -NoNewline
Write-Host "Created $EnvFile"
