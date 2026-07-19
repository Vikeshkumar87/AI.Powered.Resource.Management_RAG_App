param(
    [ValidateSet('dev', 'build', 'none')]
    [string]$FrontendMode = 'dev',
    [string]$OllamaModel = 'llama3.2',
    [switch]$ValidateOnly
)

$ErrorActionPreference = 'Stop'

function Write-Step {
    param([string]$Message)
    Write-Host "[start-all] $Message" -ForegroundColor Cyan
}

function Get-NpmCommand {
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        return 'npm'
    }

    $npmCmd = 'C:\Program Files\nodejs\npm.cmd'
    if (Test-Path $npmCmd) {
        return $npmCmd
    }

    throw 'npm was not found. Install Node.js or add npm to PATH.'
}

function Test-Ollama {
    try {
        $null = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:11434/api/tags'
        return $true
    } catch {
        return $false
    }
}

function Ensure-OllamaModel {
    param([string]$ModelName)

    $tagsJson = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:11434/api/tags' | Select-Object -ExpandProperty Content
    $tags = $tagsJson | ConvertFrom-Json

    $hasModel = $false
    foreach ($m in $tags.models) {
        if ($m.name -eq "$ModelName`:latest" -or $m.name -eq $ModelName) {
            $hasModel = $true
            break
        }
    }

    if ($hasModel) {
        Write-Step "Ollama model '$ModelName' is already available."
        return
    }

    Write-Step "Pulling Ollama model '$ModelName'..."
    $body = @{ name = $ModelName; stream = $false } | ConvertTo-Json
    $result = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:11434/api/pull' -Method Post -ContentType 'application/json' -Body $body | Select-Object -ExpandProperty Content
    Write-Step "Ollama pull result: $result"
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'
$frontendDir = Join-Path $repoRoot 'frontend-react'
$backendEntry = Join-Path $repoRoot 'backend\run.py'

if (-not (Test-Path $pythonExe)) {
    throw ".venv Python not found at $pythonExe"
}

if (-not (Test-Path $backendEntry)) {
    throw "Backend entrypoint not found at $backendEntry"
}

$npm = Get-NpmCommand

Write-Step "Repo root: $repoRoot"
Write-Step "Python: $pythonExe"
Write-Step "npm: $npm"
Write-Step "Backend entrypoint: $backendEntry"

if (-not (Test-Ollama)) {
    throw 'Ollama server is not reachable at http://127.0.0.1:11434. Start Ollama first.'
}

Write-Step 'Ollama server is reachable.'
Ensure-OllamaModel -ModelName $OllamaModel

if ($ValidateOnly) {
    Write-Step 'Validation completed. No processes started because -ValidateOnly was used.'
    exit 0
}

if ($FrontendMode -eq 'build') {
    Write-Step 'Building React frontend (frontend-react/dist)...'
    Push-Location $frontendDir
    & $npm install
    & $npm run build
    Pop-Location
}

Write-Step 'Starting FastAPI backend in a new terminal window...'
$backendCommand = "Set-Location '$repoRoot'; & '$pythonExe' '$backendEntry'"
Start-Process powershell -ArgumentList @('-NoExit', '-Command', $backendCommand) | Out-Null

if ($FrontendMode -eq 'dev') {
    Write-Step 'Starting React dev server in a new terminal window...'
    $frontendCommand = "Set-Location '$frontendDir'; & '$npm' install; & '$npm' run dev"
    Start-Process powershell -ArgumentList @('-NoExit', '-Command', $frontendCommand) | Out-Null
}

if ($FrontendMode -eq 'none') {
    Write-Step 'FrontendMode=none selected. Only backend was started.'
}

Write-Step 'Done. Backend: http://127.0.0.1:8000'
if ($FrontendMode -eq 'dev') {
    Write-Step 'React dev UI: http://localhost:5173'
} elseif ($FrontendMode -eq 'build') {
    Write-Step 'Built UI served by backend at http://127.0.0.1:8000'
}
