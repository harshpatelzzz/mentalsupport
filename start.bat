@echo off
REM NeuroSupport Startup Script for Windows

echo.
echo 🧠 NeuroSupport - Mental Health Support Platform
echo ================================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

echo ✅ Docker is installed and running
echo.

REM Check if services are already running
docker-compose ps 2>nul | findstr "Up" >nul
if not errorlevel 1 (
    echo ⚠️  Services are already running!
    echo.
    set /p RESTART="Do you want to restart them? (y/N): "
    if /i "%RESTART%"=="y" (
        echo 🔄 Restarting services...
        docker-compose down
        docker-compose up -d --build
    )
) else (
    echo 🚀 Starting services...
    docker-compose up -d --build
)

echo.
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo ✅ NeuroSupport is running!
echo.
echo 📍 Access points:
echo    🏠 Homepage:          http://localhost:3000
echo    💬 Start Chat:        http://localhost:3000/chat/start
echo    📅 Book Appointment:  http://localhost:3000/appointment/book
echo    🧑‍⚕️  Therapist Portal:  http://localhost:3000/therapist
echo    📊 Analytics:         http://localhost:3000/therapist/analytics
echo    🔌 Backend API:       http://localhost:8000
echo    📚 API Docs:          http://localhost:8000/docs
echo.
echo 📋 Useful commands:
echo    View logs:     docker-compose logs -f
echo    Stop services: docker-compose down
echo    Restart:       docker-compose restart
echo.
echo 💡 Opening homepage in your browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo Press any key to view logs (Ctrl+C to exit)...
pause >nul

docker-compose logs -f
