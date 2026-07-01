# EchoMind dev-up (Windows). Installs if needed, ingests if needed, starts both servers.
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

if (-not (Test-Path "$root\.venv")) {
    Write-Host "[echomind] creating venv + installing python deps..."
    python -m venv "$root\.venv"
    & "$root\.venv\Scripts\python.exe" -m pip install -q -r "$root\requirements.txt"
}

if (-not (Test-Path "$root\data\club_docs.json")) {
    Write-Host "[echomind] generating dataset..."
    & "$root\.venv\Scripts\python.exe" "$root\data\generate_dataset.py"
}

if (-not (Test-Path "$root\frontend\node_modules")) {
    Write-Host "[echomind] installing frontend deps..."
    Push-Location "$root\frontend"; npm install --no-audit --no-fund; Pop-Location
}

Write-Host "[echomind] starting backend on :8000 (ingests into Qdrant on first run)..."
$backend = Start-Process -PassThru -NoNewWindow "$root\.venv\Scripts\python.exe" `
    -ArgumentList "-m", "uvicorn", "backend.main:app", "--port", "8000" `
    -WorkingDirectory $root

Write-Host "[echomind] starting frontend on :3000..."
Push-Location "$root\frontend"
try {
    npm run dev
} finally {
    Pop-Location
    if ($backend -and -not $backend.HasExited) { Stop-Process -Id $backend.Id -Force }
}
