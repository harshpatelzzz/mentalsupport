#!/bin/bash

# NeuroSupport Startup Script
# This script helps start the application with proper checks

echo "🧠 NeuroSupport - Mental Health Support Platform"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "❌ Docker Compose is not available."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is installed and running"
echo ""

# Function to check if services are running
check_services() {
    echo "🔍 Checking services..."
    
    # Wait for backend
    echo -n "⏳ Waiting for backend to be ready"
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo " ✅"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Wait for frontend
    echo -n "⏳ Waiting for frontend to be ready"
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo " ✅"
            break
        fi
        echo -n "."
        sleep 2
    done
}

# Check if services are already running
if docker-compose ps | grep -q "Up"; then
    echo "⚠️  Services are already running!"
    echo ""
    read -p "Do you want to restart them? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Restarting services..."
        docker-compose down
        docker-compose up -d --build
    fi
else
    echo "🚀 Starting services..."
    docker-compose up -d --build
fi

echo ""
check_services

echo ""
echo "✅ NeuroSupport is running!"
echo ""
echo "📍 Access points:"
echo "   🏠 Homepage:          http://localhost:3000"
echo "   💬 Start Chat:        http://localhost:3000/chat/start"
echo "   📅 Book Appointment:  http://localhost:3000/appointment/book"
echo "   🧑‍⚕️  Therapist Portal:  http://localhost:3000/therapist"
echo "   📊 Analytics:         http://localhost:3000/therapist/analytics"
echo "   🔌 Backend API:       http://localhost:8000"
echo "   📚 API Docs:          http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "💡 Tip: Press Ctrl+C to stop following logs (services keep running)"
echo ""

# Follow logs
docker-compose logs -f
