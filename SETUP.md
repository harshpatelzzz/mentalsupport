# NeuroSupport Setup Guide

## Quick Start (Docker - Recommended)

### Step 1: Prerequisites
Ensure you have installed:
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose

Verify installation:
```bash
docker --version
docker-compose --version
```

### Step 2: Clone and Start

```bash
# Navigate to project directory
cd "z:/dbms projectt"

# Start all services with one command
docker-compose up --build
```

Wait for services to start. You should see:
```
✅ postgres - healthy
✅ backend - running on port 8000
✅ frontend - running on port 3000
```

### Step 3: Access Application

Open your browser:
- **Homepage**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Therapist Dashboard**: http://localhost:3000/therapist

### Step 4: Test the Application

1. **Test Anonymous Chat**:
   - Go to http://localhost:3000
   - Click "Chat Now"
   - Enter optional name or stay anonymous
   - Start chatting with AI

2. **Test Appointment Booking**:
   - Go to http://localhost:3000
   - Click "Book Appointment"
   - Select future date and time
   - Submit and get session ID

3. **Test Therapist Dashboard**:
   - Go to http://localhost:3000/therapist
   - View appointments list
   - Click "Join Chat" to join a session
   - View analytics

## Manual Setup (Without Docker)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Backend Setup

1. **Setup PostgreSQL**
```bash
# Create database
createdb neurosupport_db

# Or using psql
psql -U postgres
CREATE DATABASE neurosupport_db;
CREATE USER neurosupport WITH PASSWORD 'neurosupport123';
GRANT ALL PRIVILEGES ON DATABASE neurosupport_db TO neurosupport;
\q
```

2. **Setup Python Environment**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure Environment**
Create `backend/.env`:
```
DATABASE_URL=postgresql://neurosupport:neurosupport123@localhost:5432/neurosupport_db
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
DEBUG=true
```

4. **Run Migrations**
```bash
# From backend directory
alembic upgrade head
```

5. **Start Backend Server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend should now be running at http://localhost:8000

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Configure Environment**
Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

3. **Start Development Server**
```bash
npm run dev
```

Frontend should now be running at http://localhost:3000

## Verification Checklist

✅ **Backend Health**
- Visit http://localhost:8000
- Should see: `{"service":"NeuroSupport","version":"1.0.0","status":"running"}`
- Visit http://localhost:8000/docs for API documentation

✅ **Database Connection**
- Backend logs should show "Database initialized successfully"
- No connection errors

✅ **Frontend Loading**
- Visit http://localhost:3000
- Should see landing page with "Chat Now" and "Book Appointment" buttons

✅ **WebSocket Connection**
- Start a chat session
- Should see "Connected" indicator
- Messages should appear in real-time

✅ **Emotion Analysis**
- Send a message like "I'm feeling sad"
- Should see emotion badge (e.g., "sadness 85%")

## Common Issues & Solutions

### Issue: Port Already in Use

**Symptoms**: Error like "Address already in use"

**Solution**:
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

Or change ports in:
- `docker-compose.yml`
- Backend: `uvicorn ... --port 8001`
- Frontend: Update `.env.local`

### Issue: Database Connection Failed

**Symptoms**: "Connection refused" or "Could not connect to database"

**Solutions**:
1. Check PostgreSQL is running:
   ```bash
   # Docker
   docker-compose ps postgres
   
   # Local
   pg_isready -U neurosupport
   ```

2. Verify credentials in `.env`

3. Check DATABASE_URL format:
   ```
   postgresql://user:password@host:port/database
   ```

### Issue: Emotion Model Download Timeout

**Symptoms**: "Failed to load emotion model"

**Solutions**:
1. First run downloads ~500MB model - be patient
2. Check internet connection
3. Use fallback mode: Set `USE_FALLBACK_EMOTION=true` in `.env`

### Issue: WebSocket Connection Failed

**Symptoms**: "WebSocket disconnected" or "Connecting..." forever

**Solutions**:
1. Verify backend is running on port 8000
2. Check `NEXT_PUBLIC_WS_URL` in frontend `.env.local`
3. Disable browser extensions that block WebSockets
4. Check firewall settings

### Issue: Docker Build Fails

**Symptoms**: Build errors during `docker-compose up`

**Solutions**:
1. Clear Docker cache:
   ```bash
   docker-compose down -v
   docker system prune -a
   docker-compose up --build
   ```

2. Check Docker has enough resources (4GB+ RAM recommended)

3. Ensure all Dockerfiles exist:
   - `backend/Dockerfile`
   - `frontend/Dockerfile`

### Issue: Frontend Build Errors

**Symptoms**: `npm run build` fails

**Solutions**:
```bash
# Clean install
rm -rf node_modules .next
npm install
npm run build
```

### Issue: Alembic Migration Errors

**Symptoms**: "Can't locate revision" or migration fails

**Solutions**:
```bash
# Stamp current state
alembic stamp head

# Or reset migrations
alembic downgrade base
alembic upgrade head
```

## Development Tips

### Hot Reload
Both backend and frontend support hot reload:
- **Backend**: Changes to Python files auto-restart server
- **Frontend**: Changes to React files auto-refresh browser

### Database Management

**View tables**:
```bash
docker-compose exec postgres psql -U neurosupport -d neurosupport_db

# Inside psql
\dt                    # List tables
\d visitors            # Describe table
SELECT * FROM visitors LIMIT 5;
```

**Reset database**:
```bash
docker-compose down -v  # Deletes volumes
docker-compose up       # Fresh start
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Running Commands in Containers

```bash
# Backend shell
docker-compose exec backend sh

# Frontend shell
docker-compose exec frontend sh

# Database shell
docker-compose exec postgres psql -U neurosupport -d neurosupport_db
```

## Next Steps

After successful setup:

1. **Explore Features**:
   - Create chat sessions
   - Book appointments
   - Join as therapist
   - View analytics

2. **Customize**:
   - Modify emotion detection keywords
   - Enhance AI responses
   - Add new features

3. **Deploy**:
   - See deployment guide
   - Configure production environment
   - Setup monitoring

## Getting Help

- Check logs: `docker-compose logs -f`
- API docs: http://localhost:8000/docs
- README: See main README.md
- Issues: Open GitHub issue

## Success Criteria

Your setup is successful when:

✅ All three services running (postgres, backend, frontend)
✅ Can create chat session
✅ Messages sent and received
✅ Emotion badges appear
✅ Can book appointments
✅ Therapist dashboard loads
✅ Analytics display data

Congratulations! You're ready to use NeuroSupport! 🎉
