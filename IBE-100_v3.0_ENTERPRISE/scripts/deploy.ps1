# Deployment script for Broadcast Encoder 110
# Usage: .\scripts\deploy.ps1

param(
    [string]$Action = "deploy",
    [string]$BackupDir = "backups",
    [string]$AppDir = "."
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n[STEP] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Backup-Application {
    Write-Step "Creating backup..."
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = Join-Path $BackupDir "backup_$timestamp"
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }
    
    New-Item -ItemType Directory -Path $backupPath | Out-Null
    
    # Backup critical directories
    $itemsToBackup = @("config", "profiles", "scte35_final", "epg", "database")
    
    foreach ($item in $itemsToBackup) {
        $sourcePath = Join-Path $AppDir $item
        if (Test-Path $sourcePath) {
            $destPath = Join-Path $backupPath $item
            Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
            Write-Host "  Backed up: $item" -ForegroundColor Gray
        }
    }
    
    Write-Success "Backup created at: $backupPath"
    return $backupPath
}

function Stop-Application {
    Write-Step "Stopping application..."
    
    $processes = Get-Process | Where-Object {
        $_.ProcessName -like "*IBE*" -or 
        $_.ProcessName -like "*tsp*" -or
        $_.MainWindowTitle -like "*Broadcast Encoder*"
    }
    
    if ($processes) {
        foreach ($proc in $processes) {
            Write-Host "  Stopping: $($proc.ProcessName)" -ForegroundColor Gray
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
        Write-Success "Application stopped"
    } else {
        Write-Host "  No running instances found" -ForegroundColor Gray
    }
}

function Deploy-Application {
    Write-Step "Deploying application..."
    
    # Verify executable exists
    $exePath = Join-Path $AppDir "dist\IBE-100_Enterprise.exe"
    if (-not (Test-Path $exePath)) {
        Write-Error "Executable not found: $exePath"
        exit 1
    }
    
    Write-Success "Application ready for deployment"
    Write-Host "  Executable: $exePath" -ForegroundColor Gray
}

function Verify-Deployment {
    Write-Step "Verifying deployment..."
    
    # Check required directories
    $requiredDirs = @("config", "logs", "profiles")
    foreach ($dir in $requiredDirs) {
        $dirPath = Join-Path $AppDir $dir
        if (-not (Test-Path $dirPath)) {
            Write-Host "  Creating: $dir" -ForegroundColor Gray
            New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
        }
    }
    
    # Check TSDuck
    try {
        $tsduckVersion = & tsp --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "TSDuck is installed"
            Write-Host "  $tsduckVersion" -ForegroundColor Gray
        } else {
            Write-Error "TSDuck not found or not accessible"
        }
    } catch {
        Write-Error "TSDuck not found or not accessible"
    }
    
    Write-Success "Deployment verification complete"
}

function Start-Application {
    Write-Step "Starting application..."
    
    $exePath = Join-Path $AppDir "dist\IBE-100_Enterprise.exe"
    if (Test-Path $exePath) {
        Start-Process -FilePath $exePath -WorkingDirectory $AppDir
        Write-Success "Application started"
    } else {
        Write-Error "Executable not found: $exePath"
    }
}

# Main deployment flow
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Broadcast Encoder 110 - Deployment" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

switch ($Action.ToLower()) {
    "deploy" {
        Backup-Application
        Stop-Application
        Deploy-Application
        Verify-Deployment
        Write-Success "`nDeployment complete! You can now start the application."
    }
    "backup" {
        Backup-Application
    }
    "stop" {
        Stop-Application
    }
    "start" {
        Start-Application
    }
    "verify" {
        Verify-Deployment
    }
    "rollback" {
        Write-Step "Rollback functionality - restore from backup manually"
        Write-Host "  Backup directory: $BackupDir" -ForegroundColor Gray
        Write-Host "  Restore files from backup to application directory" -ForegroundColor Gray
    }
    default {
        Write-Error "Unknown action: $Action"
        Write-Host "`nAvailable actions:" -ForegroundColor Yellow
        Write-Host "  deploy   - Full deployment (backup, stop, deploy, verify)" -ForegroundColor Gray
        Write-Host "  backup   - Create backup only" -ForegroundColor Gray
        Write-Host "  stop     - Stop application" -ForegroundColor Gray
        Write-Host "  start    - Start application" -ForegroundColor Gray
        Write-Host "  verify   - Verify deployment" -ForegroundColor Gray
        Write-Host "  rollback - Show rollback instructions" -ForegroundColor Gray
        exit 1
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan

