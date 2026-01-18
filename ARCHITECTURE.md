# NeuroSupport Architecture Documentation

## System Overview

NeuroSupport is a modern, auth-free mental health support platform built with a microservices-inspired architecture. The system consists of three main components:

1. **Frontend** (Next.js/React/TypeScript)
2. **Backend** (FastAPI/Python)
3. **Database** (PostgreSQL)

## Architecture Principles

### 1. Auth-Free Design
- **No authentication layer** - reduces complexity and barriers to entry
- **UUID-based sessions** - each chat session identified by unique UUID
- **Anonymous by default** - users can optionally provide names
- **Session isolation** - data strictly separated by session IDs

### 2. Layered Architecture
```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│    (Next.js UI + React Components)      │
└──────────────┬──────────────────────────┘
               │ HTTP/WebSocket
┌──────────────▼──────────────────────────┐
│          API Gateway Layer              │
│       (FastAPI Routers/Routes)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Business Logic Layer            │
│            (Services)                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Data Access Layer                │
│      (SQLAlchemy Models/ORM)            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│           Database Layer                │
│           (PostgreSQL)                  │
└─────────────────────────────────────────┘
```

### 3. Separation of Concerns

Each layer has clear responsibilities:
- **Models**: Database schema definitions
- **Schemas**: Request/response validation (Pydantic)
- **Services**: Business logic and data processing
- **Routers**: HTTP endpoint definitions
- **WebSocket Manager**: Real-time connection handling

## Component Details

### Backend Architecture

#### Core Components

**Config (`app/core/`)**
- Application settings via Pydantic
- Environment variable management
- Logging configuration

**Database (`app/db/`)**
- SQLAlchemy engine setup
- Session management
- Database initialization

**Models (`app/models/`)**
- `Visitor`: Anonymous user representation
- `Appointment`: Scheduled therapy sessions
- `ChatMessage`: Real-time messages with emotion data
- `EmotionData`: Aggregated emotion analytics
- `TherapistNote`: Private therapist notes

**Services (`app/services/`)**

1. **EmotionAnalyzer**
   - Primary: HuggingFace transformer model
   - Fallback: Rule-based keyword matching
   - Returns emotion + confidence score
   
2. **ChatService**
   - Message persistence
   - AI response generation
   - Session statistics

3. **AppointmentService**
   - Appointment CRUD operations
   - Session linkage
   - Status management

4. **AnalyticsService**
   - Aggregation queries
   - Trend calculation
   - Performance metrics

**Routers (`app/routers/`)**
- RESTful API endpoints
- WebSocket endpoints
- Request validation
- Error handling

**WebSocket (`app/websocket/`)**
- Connection management
- Message broadcasting
- Typing indicators
- Session isolation

#### Data Flow: Chat Message

```
User sends message
    ↓
WebSocket receives
    ↓
Message validated
    ↓
Emotion analyzed (if visitor)
    ↓
Saved to database
    ↓
Broadcast to session participants
    ↓
AI response generated (if visitor)
    ↓
AI message saved
    ↓
Broadcast AI response
```

### Frontend Architecture

#### Structure

```
app/
├── page.tsx                 # Landing page
├── chat/
│   ├── start/              # Chat initialization
│   └── [sessionId]/        # Active chat
├── appointment/
│   └── book/               # Appointment booking
└── therapist/
    ├── page.tsx            # Dashboard
    ├── analytics/          # Analytics view
    └── session/[id]/       # Session details
```

#### State Management (Zustand)

**Chat Store**
```typescript
{
  sessionId: string | null
  visitorId: string | null
  messages: ChatMessage[]
  ws: WebSocket | null
  isConnected: boolean
  isTherapistTyping: boolean
  isAiTyping: boolean
}
```

#### Data Fetching (React Query)

- Automatic caching
- Background refetching
- Optimistic updates
- Error handling

#### WebSocket Flow

```
1. Component mounts with sessionId
2. useWebSocket hook creates connection
3. Connection stored in Zustand
4. Messages received → added to store
5. UI auto-updates (React reactivity)
6. Typing indicators managed separately
7. Connection closed on unmount
```

## Database Schema Design

### Entity Relationships

```
Visitor (1) ──────────┬───── (*) ChatMessage
                      │
                      └───── (*) Appointment (1) ───── (*) TherapistNote

Appointment (1) ─── (1) Session (via session_id)
                         │
                         └───── (*) ChatMessage (via session_id)

ChatMessage ──────── (1) EmotionData (via message_id)
```

### Key Design Decisions

1. **UUID Primary Keys**
   - Better for distributed systems
   - Non-sequential for security
   - Easier session identification

2. **Separate EmotionData Table**
   - Optimized analytics queries
   - Doesn't bloat message table
   - Can be aggregated independently

3. **Nullable visitor_id in ChatMessage**
   - Supports AI and therapist messages
   - visitor_id only for visitor messages

4. **session_id in both Appointment and ChatMessage**
   - Direct session access
   - No need for complex joins
   - Enables ad-hoc chat sessions (no appointment needed)

## Real-Time Communication

### WebSocket Architecture

```
Client                          Server
  │                               │
  ├─── WS Connect ────────────────►
  │                               ├─ Add to manager
  │                               ├─ Map to session_id
  │◄────── WS Accept ─────────────┤
  │                               │
  ├─── Send Message ──────────────►
  │                               ├─ Parse JSON
  │                               ├─ Save to DB
  │◄────── Broadcast ─────────────┤
  │                               ├─ Generate AI response
  │◄────── Broadcast AI ──────────┤
  │                               │
```

### Connection Manager

- Maps `session_id → List[WebSocket]`
- Multiple connections per session (visitor + therapists)
- Automatic cleanup on disconnect
- Thread-safe operations

## Security Architecture

### Input Validation
- Pydantic schemas validate all inputs
- SQLAlchemy ORM prevents SQL injection
- Max length constraints on text fields
- Type checking via TypeScript

### Session Isolation
- All queries filtered by session_id
- No cross-session data leakage
- UUID randomness prevents guessing

### Privacy Protection
- No PII required
- Optional name field only
- Therapist notes never exposed to visitors
- No persistent cookies or tracking

## Scalability Considerations

### Current Design Supports

✅ **Horizontal Scaling**
- Stateless backend (except WebSocket)
- Database connection pooling
- Can run multiple backend instances

⚠️ **WebSocket Scaling Limitation**
- In-memory connection manager
- Doesn't work across multiple servers
- Solution: Add Redis for pub/sub

### Database Optimization

- Indexes on frequently queried fields:
  - `session_id` (multiple tables)
  - `created_at` (for time-based queries)
  - `status` (for appointment filtering)

- Pagination support built into queries
- Limit parameters on all list endpoints

### Future Enhancements

1. **Add Redis**
   - WebSocket pub/sub
   - Session caching
   - Rate limiting

2. **Message Queue**
   - Async emotion analysis
   - Email notifications
   - Background tasks

3. **Load Balancer**
   - Distribute traffic
   - Health checks
   - Sticky sessions for WebSocket

## Deployment Architecture

### Development
```
Docker Compose
├── PostgreSQL (port 5432)
├── Backend (port 8000)
└── Frontend (port 3000)
```

### Production (Recommended)
```
                    ┌──────────────┐
                    │ Load Balancer│
                    └───────┬──────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼─────┐       ┌────▼─────┐       ┌────▼─────┐
   │Frontend 1│       │Frontend 2│       │Frontend N│
   └──────────┘       └──────────┘       └──────────┘
                            │
                    ┌───────▼────────┐
                    │  API Gateway   │
                    └───────┬────────┘
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼─────┐       ┌────▼─────┐       ┌────▼─────┐
   │Backend 1 │       │Backend 2 │       │Backend N │
   └────┬─────┘       └────┬─────┘       └────┬─────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │    Redis       │ (Session/Cache)
                    └────────────────┘
                            │
                    ┌───────▼────────┐
                    │   PostgreSQL   │ (Primary + Replicas)
                    └────────────────┘
```

## Technology Choices Rationale

### FastAPI
- **Pros**: Fast, modern, automatic docs, async support, type hints
- **Use case**: RESTful API + WebSocket server

### Next.js
- **Pros**: SSR/SSG, routing, optimized builds, great DX
- **Use case**: Modern React framework with App Router

### PostgreSQL
- **Pros**: ACID, JSON support, reliable, excellent ORM support
- **Use case**: Relational data with complex queries

### SQLAlchemy
- **Pros**: Mature ORM, type-safe, migration support (Alembic)
- **Use case**: Database abstraction and modeling

### Zustand
- **Pros**: Simple, no boilerplate, TypeScript friendly
- **Use case**: Client-side state (smaller than Redux)

### React Query
- **Pros**: Caching, refetching, automatic retries
- **Use case**: Server state management

### Tailwind CSS
- **Pros**: Utility-first, fast development, consistent design
- **Use case**: Responsive, modern UI styling

## Best Practices Implemented

1. **Type Safety**
   - TypeScript on frontend
   - Pydantic on backend
   - SQLAlchemy models typed

2. **Error Handling**
   - Try-catch blocks
   - Graceful degradation
   - User-friendly messages

3. **Code Organization**
   - Single Responsibility Principle
   - DRY (Don't Repeat Yourself)
   - Clear file structure

4. **Documentation**
   - Inline comments for complex logic
   - Docstrings for functions
   - OpenAPI auto-generated docs

5. **Version Control**
   - .gitignore configured
   - Alembic for schema versioning
   - Docker for environment consistency

---

This architecture provides a solid foundation for a mental health support platform while remaining flexible for future enhancements.
