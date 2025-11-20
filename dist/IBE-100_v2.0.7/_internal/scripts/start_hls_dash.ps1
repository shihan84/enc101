# IBE-100 - Start HLS/DASH Output and Serve Over HTTP
param(
    [string]$InputUrl = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
    [string]$OutDir = "E:\Streams\hls",
    [int]$SegmentDuration = 6,
    [int]$PlaylistWindow = 5,
    [switch]$Dash,
    [int]$HttpPort = 8080
)

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "IBE-100 - HLS/DASH Output Starter" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Ensure output directory exists
if (!(Test-Path $OutDir)) {
    Write-Host "Creating output directory: $OutDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
}

# Find tsp
$tspPath = "tsp"
if (Test-Path "C:\Program Files\TSDuck\bin\tsp.exe") { $tspPath = "C:\Program Files\TSDuck\bin\tsp.exe" }
elseif (Get-Command tsp -ErrorAction SilentlyContinue) { $tspPath = (Get-Command tsp).Source }

Write-Host "Using tsp: $tspPath" -ForegroundColor Green

# Build tsp command
$cmd = @()
$cmd += '"' + $tspPath + '"'
$cmd += '-I'
$cmd += 'hls'
$cmd += '"' + $InputUrl + '"'

# Minimal PMT add (helps players recognize PIDs)
$cmd += '-P'
$cmd += 'pmt'
$cmd += '--service'; $cmd += '1'
$cmd += '--add-pid'; $cmd += '256/0x1b'
$cmd += '--add-pid'; $cmd += '257/0x0f'

# Output plugin
$cmd += '-O'
$cmd += 'hls'
$cmd += '--live'
$cmd += '"' + $OutDir + '"'
$cmd += '--segment-duration'; $cmd += $SegmentDuration
$cmd += '--playlist-window'; $cmd += $PlaylistWindow
$cmd += '--cors'; $cmd += '*'
if ($Dash) { $cmd += '--dash' }

$cmdLine = $cmd -join ' '
Write-Host "\nLaunching TSDuck:\n$cmdLine\n" -ForegroundColor Green

# Start tsp in separate window
Start-Process powershell -ArgumentList "-NoExit","-Command","$cmdLine" -WindowStyle Normal

Start-Sleep -Seconds 2

# Start simple HTTP server in OutDir
Write-Host "Starting HTTP server on port $HttpPort to serve: $OutDir" -ForegroundColor Green
$python = 'python'
if (-not (Get-Command $python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found in PATH. Install Python or serve with another web server." -ForegroundColor Red
    exit 1
}

Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$OutDir'; $python -m http.server $HttpPort" -WindowStyle Normal

$hlsUrl = "http://localhost:$HttpPort/index.m3u8"
$dashUrl = "http://localhost:$HttpPort/manifest.mpd"

Write-Host "\nAccess URLs:" -ForegroundColor Cyan
Write-Host "  HLS:  $hlsUrl" -ForegroundColor White
if ($Dash) { Write-Host "  DASH: $dashUrl" -ForegroundColor White }

Write-Host "\nTip: Open in VLC or browser (browser requires http)." -ForegroundColor Yellow
