# NeuroSupport - Quick Reference

## 🚀 Start Commands

### Windows
```cmd
start.bat
```

### Mac/Linux
```bash
chmod +x start.sh
./start.sh
```

### Manual
```bash
docker-compose up --build
```

## 🔗 Access URLs

| Service | URL |
|---------|-----|
| Homepage | http://localhost:3000 |
| Chat | http://localhost:3000/chat/start |
| Appointments | http://localhost:3000/appointment/book |
| Therapist | http://localhost:3000/therapist |
| Analytics | http://localhost:3000/therapist/analytics |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Start with rebuild
docker-compose up -d --build

# Stop services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Restart a service
docker-compose restart backend

# Access service shell
docker-compose exec backend sh
docker-compose exec frontend sh

# Database shell
docker-compose exec postgres psql -U neurosupport -d neurosupport_db
```

## 💾 Database Commands

### Inside PostgreSQL shell
```sql
-- List tables
\dt

-- Describe table
\d visitors
\d appointments
\d chat_messages

-- View data
SELECT * FROM visitors LIMIT 10;
SELECT * FROM appointments ORDER BY created_at DESC;
SELECT * FROM chat_messages WHERE session_id = 'your-uuid';

-- Count records
SELECT COUNT(*) FROM visitors;
SELECT COUNT(*) FROM chat_messages;

-- Emotion stats
SELECT emotion, COUNT(*) FROM emotion_data GROUP BY emotion;

-- Exit
\q
```

### Alembic Migrations
```bash
# Create migration (from backend directory)
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View current version
alembic current

# View history
alembic history
```

## 🛠️ Development Commands

### Backend
```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload

# Run with different port
uvicorn app.main:app --reload --port 8001

# Run tests (when implemented)
pytest
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Run tests (when implemented)
npm test
```

## 📊 Common Queries

### Check service health
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# All services status
docker-compose ps
```

### View active sessions
```bash
curl http://localhost:8000/api/therapist/active-sessions
```

### Get appointments
```bash
curl http://localhost:8000/api/appointments/
```

### Get analytics
```bash
curl http://localhost:8000/api/analytics/summary
```

## 🔍 Troubleshooting Quick Fixes

### Port already in use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Docker issues
```bash
# Clean everything
docker-compose down -v
docker system prune -a
docker-compose up --build

# Restart Docker Desktop (Windows/Mac)
```

### Database connection failed
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres

# Fresh database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

### Frontend won't load
```bash
# Clear and reinstall
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://neurosupport:neurosupport123@postgres:5432/neurosupport_db
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
DEBUG=true
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 🧪 Testing Workflows

### Test Chat Flow
1. Go to http://localhost:3000
2. Click "Chat Now"
3. Optional: Enter name
4. Send message: "I'm feeling anxious"
5. Check emotion badge appears
6. AI should respond

### Test Appointment Flow
1. Go to http://localhost:3000
2. Click "Book Appointment"
3. Select future date/time
4. Submit
5. Note session ID
6. Click "Start Chatting Now"

### Test Therapist Flow
1. Go to http://localhost:3000/therapist
2. View appointments list
3. Click "Join Chat" on active session
4. Send message as therapist
5. Go to session details
6. Add private note

## 🎯 Production Checklist

Before deploying to production:

- [ ] Update DATABASE_URL with production database
- [ ] Set DEBUG=false
- [ ] Configure CORS for production domain
- [ ] Set up environment variables securely
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure logging/monitoring
- [ ] Review security settings
- [ ] Test all features
- [ ] Load test WebSocket connections

## 📚 File Locations

### Configuration
- `docker-compose.yml` - Service orchestration
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies
- `backend/alembic.ini` - Migration config

### Code
- `backend/app/` - Backend source
- `frontend/app/` - Frontend pages
- `frontend/components/` - React components
- `frontend/services/api.ts` - API client

### Documentation
- `README.md` - Main docs
- `SETUP.md` - Setup guide
- `ARCHITECTURE.md` - System design
- `PROJECT_SUMMARY.md` - Overview

## ⌨️ VS Code Shortcuts (Optional)

If using VS Code:
- `Ctrl+~` - Toggle terminal
- `Ctrl+P` - Quick file open
- `F5` - Start debugging
- `Ctrl+Shift+P` - Command palette

## 📞 Quick Help

- API Documentation: http://localhost:8000/docs
- View logs: `docker-compose logs -f`
- Restart everything: `docker-compose restart`
- Fresh start: `docker-compose down -v && docker-compose up --build`

## 💡 Pro Tips

1. **Keep Docker Desktop running** for best performance
2. **Use API docs** at `/docs` for testing endpoints
3. **Check logs first** when debugging issues
4. **Fresh start** solves 90% of issues
5. **Save session IDs** for testing therapist features

---

Keep this file handy for quick reference! 🚀
