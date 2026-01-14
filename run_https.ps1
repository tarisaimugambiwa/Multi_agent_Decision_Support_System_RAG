# Start Django Development Server with HTTPS
# SSL Certificate expires: 365 days from creation

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Django HTTPS Server" -ForegroundColor Green
Write-Host "SSL Certificate valid for 365 days" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor White
Write-Host "  - Local:   https://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  - Network: https://192.168.14.240:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Browser Security Warning:" -ForegroundColor Yellow
Write-Host "   You'll see a warning because this is a self-signed certificate." -ForegroundColor Gray
Write-Host "   Click 'Advanced' and then 'Proceed to site' to continue." -ForegroundColor Gray
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor DarkGray
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Run the HTTPS server using django-sslserver
.\venv\Scripts\python.exe manage.py runsslserver --certificate ssl\cert.pem --key ssl\key.pem 0.0.0.0:8000
