# Kill existing SignalRApp processes
Write-Host "Killing any running SignalRApp processes..." -ForegroundColor Yellow
Get-Process -Name "SignalRApp" -ErrorAction SilentlyContinue | ForEach-Object { 
    Write-Host "Killing process: $($_.Id)" -ForegroundColor Red
    $_ | Stop-Process -Force 
}

# Wait a moment for processes to terminate
Start-Sleep -Seconds 2

# Build the application
Write-Host "Building the application..." -ForegroundColor Green
dotnet build

# Ensure JSON files are copied
Write-Host "Ensuring JSON files are in output directory..." -ForegroundColor Cyan
$outputDir = "bin\Debug\net9.0"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

Copy-Item -Path "message_data.json" -Destination "$outputDir\message_data.json" -Force
Copy-Item -Path "example_message.json" -Destination "$outputDir\example_message.json" -Force

Write-Host "JSON files copied:" -ForegroundColor Green
Get-ChildItem -Path "$outputDir\*.json" | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor White
}

Write-Host "Build process completed." -ForegroundColor Green
