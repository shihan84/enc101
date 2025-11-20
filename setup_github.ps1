# GitHub Repository Setup Script
# This script helps you set up the GitHub repository with PAT authentication

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubRepoUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$PersonalAccessToken
)

Write-Host "🚀 Setting up GitHub repository..." -ForegroundColor Green
Write-Host ""

# Extract repository name from URL
if ($GitHubRepoUrl -match "github\.com[/:](.+)/(.+)\.git") {
    $username = $matches[1]
    $repo = $matches[2]
    $authenticatedUrl = "https://$PersonalAccessToken@github.com/$username/$repo.git"
} elseif ($GitHubRepoUrl -match "github\.com/(.+)/(.+)") {
    $username = $matches[1]
    $repo = $matches[2]
    $authenticatedUrl = "https://$PersonalAccessToken@github.com/$username/$repo.git"
} else {
    Write-Host "❌ Invalid GitHub repository URL format" -ForegroundColor Red
    Write-Host "Expected format: https://github.com/username/repo.git or https://github.com/username/repo" -ForegroundColor Yellow
    exit 1
}

# Add remote origin
Write-Host "📡 Adding remote origin..." -ForegroundColor Cyan
git remote add origin $authenticatedUrl
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Remote might already exist, updating..." -ForegroundColor Yellow
    git remote set-url origin $authenticatedUrl
}

# Stage all files
Write-Host "📦 Staging all files..." -ForegroundColor Cyan
git add .

# Create initial commit
Write-Host "💾 Creating initial commit..." -ForegroundColor Cyan
git commit -m "Initial commit: Broadcast Encoder 110 Enterprise v3.0"

# Push to GitHub
Write-Host "⬆️  Pushing to GitHub..." -ForegroundColor Cyan
git branch -M main
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository: $GitHubRepoUrl" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Failed to push to GitHub. Please check:" -ForegroundColor Red
    Write-Host "  1. Repository URL is correct" -ForegroundColor Yellow
    Write-Host "  2. PAT has repository write permissions" -ForegroundColor Yellow
    Write-Host "  3. Repository exists on GitHub" -ForegroundColor Yellow
}

