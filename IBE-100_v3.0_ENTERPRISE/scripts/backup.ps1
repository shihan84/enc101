# Automated backup script for Broadcast Encoder 110
# Usage: .\scripts\backup.ps1

param(
    [string]$BackupType = "full",
    [string]$BackupDir = "backups",
    [int]$MaxBackups = 10
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Backup-Database {
    Write-Step "Backing up database..."
    
    $dbPath = "database\sessions.db"
    if (-not (Test-Path $dbPath)) {
        Write-Host "  Database not found, skipping..." -ForegroundColor Gray
        return
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = Join-Path $BackupDir "database_$timestamp.db"
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }
    
    Copy-Item -Path $dbPath -Destination $backupPath -Force
    Write-Success "Database backed up to: $backupPath"
}

function Backup-Config {
    Write-Step "Backing up configuration..."
    
    $configDir = "config"
    if (-not (Test-Path $configDir)) {
        Write-Host "  Config directory not found, skipping..." -ForegroundColor Gray
        return
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = Join-Path $BackupDir "config_$timestamp"
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }
    
    Copy-Item -Path $configDir -Destination $backupPath -Recurse -Force
    Write-Success "Configuration backed up to: $backupPath"
}

function Backup-Profiles {
    Write-Step "Backing up profiles..."
    
    $profilesDir = "profiles"
    if (-not (Test-Path $profilesDir)) {
        Write-Host "  Profiles directory not found, skipping..." -ForegroundColor Gray
        return
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = Join-Path $BackupDir "profiles_$timestamp"
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }
    
    Copy-Item -Path $profilesDir -Destination $backupPath -Recurse -Force
    Write-Success "Profiles backed up to: $backupPath"
}

function Cleanup-OldBackups {
    Write-Step "Cleaning up old backups (keeping last $MaxBackups)..."
    
    if (-not (Test-Path $BackupDir)) {
        return
    }
    
    $backups = Get-ChildItem -Path $BackupDir | 
        Sort-Object LastWriteTime -Descending | 
        Select-Object -Skip $MaxBackups
    
    foreach ($backup in $backups) {
        Write-Host "  Removing: $($backup.Name)" -ForegroundColor Gray
        Remove-Item -Path $backup.FullName -Recurse -Force
    }
    
    Write-Success "Cleanup complete"
}

# Main backup flow
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Broadcast Encoder 110 - Backup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

switch ($BackupType.ToLower()) {
    "full" {
        Backup-Database
        Backup-Config
        Backup-Profiles
    }
    "database" {
        Backup-Database
    }
    "config" {
        Backup-Config
    }
    "profiles" {
        Backup-Profiles
    }
    default {
        Write-Error "Unknown backup type: $BackupType"
        Write-Host "`nAvailable types:" -ForegroundColor Yellow
        Write-Host "  full     - Backup everything" -ForegroundColor Gray
        Write-Host "  database - Backup database only" -ForegroundColor Gray
        Write-Host "  config   - Backup configuration only" -ForegroundColor Gray
        Write-Host "  profiles - Backup profiles only" -ForegroundColor Gray
        exit 1
    }
}

Cleanup-OldBackups

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Success "Backup complete!"

