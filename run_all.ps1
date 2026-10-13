param(
    [switch]$RebuildData,
    [switch]$SkipShap
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $projectRoot

$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Project environment not found. Create .venv and install requirements.txt first."
}

$env:PYTHONPATH = Join-Path $projectRoot "src"

function Invoke-PythonStage {
    param(
        [string]$Name,
        [string[]]$Arguments
    )

    Write-Host ""
    Write-Host "==> $Name" -ForegroundColor Cyan
    & $script:pythonPath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Stage '$Name' failed with exit code $LASTEXITCODE."
    }
}

$snapshotPath = Join-Path $projectRoot "data\processed\oulad_day40.csv"
$rawVlePath = Join-Path $projectRoot "data\raw\oulad\studentVle.csv"

if ($RebuildData -or -not (Test-Path -LiteralPath $snapshotPath)) {
    if (-not (Test-Path -LiteralPath $rawVlePath)) {
        throw "OULAD raw files are missing from data\raw\oulad."
    }
    Write-Host "The raw VLE file is about 454 MB. This stage can take a while; progress will be printed." -ForegroundColor Yellow
    Invoke-PythonStage -Name "Build day-40 dataset" -Arguments @(
        "-m", "student_success.oulad_features",
        "data/raw/oulad", "data/processed/oulad_day40.csv", "--cutoff-day", "40"
    )
} else {
    Write-Host "==> Using cached data\processed\oulad_day40.csv" -ForegroundColor Green
    Write-Host "    Use .\run_all.ps1 -RebuildData only when the raw data or feature code changes."
}

Invoke-PythonStage -Name "Generate EDA artifacts" -Arguments @(
    "-m", "student_success.eda_oulad",
    "data/processed/oulad_day40.csv", "--output-dir", "artifacts/eda"
)
Invoke-PythonStage -Name "Train and evaluate models" -Arguments @(
    "-m", "student_success.train_oulad",
    "data/processed/oulad_day40.csv", "--config", "config/oulad_model.json", "--output-dir", "artifacts/oulad"
)
Invoke-PythonStage -Name "Build faculty review queue" -Arguments @(
    "-m", "student_success.support_outputs",
    "artifacts/oulad/test_predictions.csv", "artifacts/oulad/faculty_review_queue.csv"
)

if ($SkipShap) {
    Write-Host "==> Skipping SHAP regeneration because -SkipShap was supplied" -ForegroundColor Yellow
} else {
    Invoke-PythonStage -Name "Generate SHAP explanations" -Arguments @(
        "-m", "student_success.explain_oulad",
        "--output-dir", "artifacts/oulad/explanations", "--rows-per-tier", "25"
    )
}

Invoke-PythonStage -Name "Run automated tests" -Arguments @("-m", "pytest", "-q")

Write-Output "Complete: artifacts are available in artifacts/eda and artifacts/oulad."
