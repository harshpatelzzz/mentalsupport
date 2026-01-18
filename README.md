# NeuroSupport - Mental Health Support Platform

A production-ready, full-stack mental health support platform with real-time chat, emotion analysis, and appointment booking. **Completely auth-free** - users are identified by UUID session IDs only.

## 🎯 Features

### Core Capabilities
- **Anonymous Chat**: Start chatting immediately without any login or signup
- **AI Support Bot**: Intelligent chatbot with emotion detection
- **Therapist Integration**: Therapists can join any active chat session
- **Appointment Booking**: Schedule sessions with professional therapists
- **Emotion Analysis**: Real-time emotion detection using HuggingFace transformers
- **Analytics Dashboard**: Comprehensive insights and visualizations
- **Private Notes**: Therapist-only session notes (not visible to visitors)

### Technical Highlights
- Real-time WebSocket communication
- Clean layered architecture
- Type-safe with TypeScript
- Responsive, modern UI with Tailwind CSS
- Production-ready Docker setup
- Database migrations with Alembic
- Comprehensive error handling

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI (Python web framework)
- PostgreSQL (Database)
- SQLAlchemy (ORM)
- Alembic (Migrations)
- WebSockets (Real-time)
- HuggingFace Transformers (AI/ML)

**Frontend:**
- Next.js 14 (React framework)
- TypeScript
- Tailwind CSS
- React Query (Data fetching)
- Zustand (State management)
- Chart.js (Analytics visualizations)

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL 15

## 📁 Project Structure

```
neurosupport/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, logging
│   │   ├── db/             # Database setup
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── routers/        # API endpoints
│   │   ├── websocket/      # WebSocket manager
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                # Next.js pages (App Router)
│   ├── components/         # React components
│   ├── hooks/              # Custom hooks
│   ├── services/           # API client
│   ├── store/              # Zustand stores
│   ├── lib/                # Utilities
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- OR: Python 3.11+, Node.js 18+, PostgreSQL 15

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd neurosupport
```

2. **Start all services**
```bash
docker-compose up --build
```

3. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

That's it! The application will automatically:
- Start PostgreSQL
- Run database migrations
- Start the FastAPI backend
- Start the Next.js frontend

### Option 2: Local Development

#### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup database**
```bash
# Make sure PostgreSQL is running
createdb neurosupport_db

# Run migrations
alembic upgrade head
```

4. **Create .env file**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Start the server**
```bash
uvicorn app.main:app --reload
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Create .env.local**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

3. **Start the development server**
```bash
npm run dev
```

## 🎮 User Flows

### For Visitors (Anonymous Users)

1. **Quick Chat**
   - Go to homepage
   - Click "Chat Now"
   - Optionally enter a name (or stay anonymous)
   - Start chatting with AI support
   - Therapist can join anytime

2. **Book Appointment**
   - Go to homepage
   - Click "Book Appointment"
   - Select date and time
   - Optionally enter name
   - Get instant session ID
   - Chat opens automatically

### For Therapists

1. **View Dashboard**
   - Navigate to `/therapist`
   - See all appointments
   - View active chat sessions

2. **Join Chat**
   - Click "Join Chat" on any appointment
   - Real-time messaging with visitor
   - View emotion analysis in real-time

3. **Session Management**
   - View session details
   - See emotion timeline charts
   - Write private notes
   - Update appointment status

4. **Analytics**
   - View comprehensive metrics
   - Emotion distribution charts
   - Session trends over time
   - Performance indicators

## 📊 Database Schema

### Tables

**visitors**
- id (UUID, PK)
- name (String, nullable)
- created_at (DateTime)

**appointments**
- id (UUID, PK)
- visitor_id (UUID, FK)
- session_id (UUID, unique)
- start_time (DateTime with timezone)
- end_time (DateTime, nullable)
- status (Enum: scheduled, completed, cancelled)
- created_at, updated_at (DateTime)

**chat_messages**
- id (UUID, PK)
- session_id (UUID)
- visitor_id (UUID, FK, nullable)
- sender_type (Enum: visitor, therapist, ai)
- content (Text)
- emotion (String, nullable)
- confidence (Float, nullable)
- is_read (String)
- created_at (DateTime)

**emotion_data**
- id (UUID, PK)
- session_id (UUID)
- message_id (UUID)
- emotion (String)
- confidence (Float)
- message_content (Text, truncated)
- created_at (DateTime)

**therapist_notes**
- id (UUID, PK)
- appointment_id (UUID, FK)
- note (Text)
- created_at, updated_at (DateTime)

## 🔌 API Endpoints

### Chat
- `POST /api/chat/session/create` - Create new chat session
- `GET /api/chat/messages/{session_id}` - Get chat history
- `POST /api/chat/messages` - Send message (HTTP fallback)
- `WS /api/chat/ws/{session_id}` - WebSocket connection

### Appointments
- `POST /api/appointments/` - Create appointment
- `GET /api/appointments/` - List all appointments
- `GET /api/appointments/upcoming` - Get upcoming appointments
- `GET /api/appointments/{id}` - Get appointment details
- `PATCH /api/appointments/{id}` - Update appointment

### Therapist
- `POST /api/therapist/notes` - Create private note
- `GET /api/therapist/notes/appointment/{id}` - Get appointment notes
- `GET /api/therapist/emotion-timeline/{session_id}` - Get emotion data
- `GET /api/therapist/active-sessions` - List active sessions

### Analytics
- `GET /api/analytics/summary` - Get comprehensive analytics

Full API documentation available at: http://localhost:8000/docs

## 🤖 Emotion Analysis

The platform uses a hybrid approach for emotion detection:

1. **Primary: HuggingFace Transformer**
   - Model: `j-hartmann/emotion-english-distilroberta-base`
   - Detects: joy, sadness, anger, fear, surprise, disgust, neutral
   - Returns confidence score (0-1)

2. **Fallback: Rule-based Detection**
   - Keyword matching
   - Sentiment analysis
   - Activated if transformer fails

Emotions are:
- Analyzed per message
- Stored with confidence scores
- Visualized in therapist dashboard
- Used for trend analysis

## 🔒 Security & Privacy

### Auth-Free Design
- No user accounts or passwords
- UUID-based session identification
- No personal data collection required
- Anonymous by default

### Security Measures
- Input sanitization (Pydantic validation)
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (React escaping)
- CORS configuration
- Rate limiting ready (implement as needed)
- Secure WebSocket handling

### Privacy
- Optional name field only
- No email or phone required
- Session data isolated by UUID
- Therapist notes are private
- No cross-session data leakage

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📈 Monitoring & Logs

- **Backend logs**: Console output via uvicorn
- **Frontend logs**: Browser console + server logs
- **Database**: PostgreSQL logs
- **Docker logs**: `docker-compose logs -f`

## 🛠️ Development

### Adding Database Models

1. Create model in `backend/app/models/`
2. Import in `backend/app/db/base.py`
3. Generate migration: `alembic revision --autogenerate -m "description"`
4. Review migration in `alembic/versions/`
5. Apply: `alembic upgrade head`

### Adding API Endpoints

1. Create router in `backend/app/routers/`
2. Include in `backend/app/main.py`
3. Add API client function in `frontend/services/api.ts`
4. Use with React Query in components

### Adding Frontend Pages

1. Create page in `frontend/app/`
2. Add navigation links
3. Implement with TypeScript
4. Style with Tailwind CSS

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up

# Build and start
docker-compose up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service]

# Restart a service
docker-compose restart [service]

# Access shell
docker-compose exec backend sh
docker-compose exec frontend sh

# Database shell
docker-compose exec postgres psql -U neurosupport -d neurosupport_db
```

## 🚨 Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in environment variables
- Verify database credentials
- Check port 5432 is not in use

### WebSocket Connection Failed
- Check backend is running on port 8000
- Verify CORS settings
- Check firewall rules
- Ensure `WS_URL` is correct

### Frontend Build Errors
- Delete `node_modules` and `.next`
- Run `npm install` again
- Check Node.js version (18+)

### Emotion Model Loading Slow
- First load downloads model (~500MB)
- Subsequent loads are faster
- Set `USE_FALLBACK_EMOTION=true` for rule-based only

## 📝 Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
DEBUG=true
EMOTION_MODEL=j-hartmann/emotion-english-distilroberta-base
USE_FALLBACK_EMOTION=false
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

NeuroSupport is a demonstration platform for educational purposes. It provides supportive conversations but is **not a substitute for professional medical advice, diagnosis, or treatment**. 

If you're in crisis:
- Call emergency services (911)
- Contact a crisis hotline
- Visit the nearest emergency room

## 🙏 Acknowledgments

- HuggingFace for emotion detection models
- FastAPI and Next.js communities
- All contributors and supporters

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the documentation
- Review the API docs at `/docs`

---

Built with ❤️ for mental health support
