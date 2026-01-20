# 🧑‍⚕️ Therapist/Bot Chat Routing System

## ✅ **FEATURE COMPLETE**

The bot now **automatically stops responding** when a therapist joins a chat session.

---

## 🎯 **How It Works**

### **Session States:**

| Mode | Bot Responds? | Therapist Active? |
|------|---------------|-------------------|
| `BOT_ONLY` | ✅ Yes | ❌ No |
| `THERAPIST_JOINED` | ❌ No | ✅ Yes |

---

## 🔄 **User Flow**

### **Step 1: User Starts Chat**
```
User opens: http://localhost:3000
  ↓
Clicks "Chat Now"
  ↓
Session created with mode: BOT_ONLY
  ↓
User types: "I'm feeling stressed"
  ↓
Bot responds: "I hear you. Tell me more..."
```

### **Step 2: Therapist Joins**
```
Therapist opens: http://localhost:3000/therapist
  ↓
Finds session in appointments list
  ↓
Clicks "Join Chat"
  ↓
Redirects to: /chat/{sessionId}?therapist=true
  ↓
Frontend calls: POST /api/chat/session/{id}/therapist-join
  ↓
Backend updates: mode = THERAPIST_JOINED
  ↓
System message sent: "🧑‍⚕️ A therapist has joined the chat. The bot will no longer respond."
  ↓
User sees system message in chat
```

### **Step 3: Direct Communication**
```
User types: "Hello therapist"
  ↓
Backend checks session mode: THERAPIST_JOINED
  ↓
Bot skips AI response ✅
  ↓
Message broadcast to all (including therapist)
  ↓
Therapist sees message
  ↓
Therapist types: "Hello! I'm here to help"
  ↓
Message broadcast with sender_type: "therapist"
  ↓
User sees therapist message ✅
```

---

## 🏗️ **Technical Architecture**

### **Database Model**

**Table:** `chat_sessions`

```sql
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY,
  session_id UUID UNIQUE NOT NULL,
  mode VARCHAR (bot_only | therapist_joined),
  therapist_joined_at TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**Purpose:** Track whether bot or therapist is active in each session.

---

### **Backend Logic**

#### **WebSocket Handler** (`backend/app/routers/chat.py`)

```python
# When user sends message:
if sender_type == "visitor":
    # Get session state
    chat_session = get_or_create_session(session_id)
    
    # Check mode BEFORE generating AI response
    if chat_session.mode == SessionMode.THERAPIST_JOINED:
        logger.info("🧑‍⚕️ Therapist active - Bot will NOT respond")
        continue  # Skip AI generation
    
    # Generate bot response (only if BOT_ONLY mode)
    ai_response = generate_ai_response(message)
    broadcast(ai_response)
```

#### **Therapist Join Endpoint** (`POST /api/chat/session/{id}/therapist-join`)

```python
@router.post("/session/{session_id}/therapist-join")
async def therapist_join_session(session_id: UUID, db: Session):
    # Get or create session
    chat_session = get_or_create_session(session_id)
    
    # Update mode
    chat_session.mode = SessionMode.THERAPIST_JOINED
    chat_session.therapist_joined_at = datetime.utcnow()
    db.commit()
    
    # Notify user
    await broadcast_system_message({
        "type": "SYSTEM_MESSAGE",
        "message": "🧑‍⚕️ A therapist has joined the chat..."
    })
```

---

### **Frontend Logic**

#### **Therapist Detection** (`frontend/app/chat/[sessionId]/page.tsx`)

```typescript
const searchParams = useSearchParams()
const isTherapist = searchParams.get('therapist') === 'true'

// Call join endpoint when therapist opens chat
useEffect(() => {
  if (isTherapist && sessionId) {
    await chatApi.therapistJoinSession(sessionId)
  }
}, [isTherapist, sessionId])

// Send messages with correct sender type
const handleSendMessage = () => {
  const senderType = isTherapist ? 'therapist' : 'visitor'
  sendMessage(input, senderType)
}
```

#### **System Message Display** (`frontend/hooks/useWebSocket.ts`)

```typescript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  
  if (data.type === 'SYSTEM_MESSAGE') {
    // Display as chat message
    const systemMessage = {
      sender_type: 'ai',  // Styled like bot
      content: data.message,
      // ...
    }
    addMessage(systemMessage)
  }
}
```

---

## 🧪 **Testing the Feature**

### **Test 1: Bot-Only Mode (Default)**

1. Open http://localhost:3000
2. Click "Chat Now"
3. Type: `"I'm feeling stressed"`
4. **Expected:** Bot responds with supportive message ✅

### **Test 2: Therapist Joins**

1. Keep user chat open (Step 1 above)
2. Open new tab: http://localhost:3000/therapist
3. Find the session in appointments
4. Click "Join Chat"
5. **Expected in user's chat:** 
   - System message: "🧑‍⚕️ A therapist has joined..." ✅
   - No more bot responses ✅

### **Test 3: Direct Communication**

1. Continue from Test 2
2. In **user's tab**, type: `"Hello therapist"`
3. **Expected:** 
   - Message appears in both tabs ✅
   - Bot does NOT respond ✅
4. In **therapist's tab**, type: `"Hello! I'm here to help"`
5. **Expected:** 
   - Message appears in user's tab with therapist icon ✅
   - Bot still does NOT respond ✅

### **Test 4: Cross-Tab Sync**

1. Open user chat in 3 different browser tabs
2. Therapist joins in 4th tab
3. **Expected:** 
   - System message appears in ALL 3 user tabs ✅
   - Bot stops in ALL tabs ✅
   - Works via WebSocket broadcast ✅

---

## 📊 **Backend Logs**

### **When Bot is Active:**

```
INFO - Processing visitor message in session abc-123
INFO - 🤖 Bot mode active in session abc-123 - Generating AI response
INFO - AI response generated: "I'm here to listen..."
```

### **When Therapist Joins:**

```
INFO - 🧑‍⚕️ Therapist joining session abc-123
INFO - ✅ Session abc-123 mode changed to THERAPIST_JOINED
INFO - 📢 Sent therapist join notification to session abc-123
```

### **When User Sends Message After Therapist Joins:**

```
INFO - Processing visitor message in session abc-123
INFO - 🧑‍⚕️ Therapist active in session abc-123 - Bot will NOT respond
```

**No "Generating AI response" log appears!** ✅

---

## 🔧 **API Endpoints**

### **POST /api/chat/session/{session_id}/therapist-join**

**Purpose:** Therapist joins session, disables bot.

**Request:**
```http
POST /api/chat/session/abc-123/therapist-join
```

**Response:**
```json
{
  "status": "success",
  "session_id": "abc-123",
  "mode": "therapist_joined",
  "therapist_joined_at": "2026-01-20T12:00:00Z"
}
```

**Side Effects:**
1. Updates `chat_sessions.mode` to `THERAPIST_JOINED`
2. Sets `therapist_joined_at` timestamp
3. Broadcasts `SYSTEM_MESSAGE` to all session participants

---

## 🎨 **Frontend UI Changes**

### **System Message Styling**

System messages appear as special chat bubbles:

```
┌─────────────────────────────────────────┐
│ 🤖 Bot                                  │
│ I'm here to listen...                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🧑‍⚕️ SYSTEM                              │
│ A therapist has joined the chat.        │
│ The bot will no longer respond.         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🧑‍⚕️ Therapist                           │
│ Hello! I'm here to help you.            │
└─────────────────────────────────────────┘
```

---

## ✅ **Guarantees**

1. ✅ **Bot NEVER responds after therapist joins**
2. ✅ **Mode persists across page reloads** (stored in DB)
3. ✅ **Works across multiple browser tabs** (WebSocket broadcast)
4. ✅ **No authentication required** (uses query param)
5. ✅ **System message notifies user**
6. ✅ **Sender types are correctly identified** (visitor/therapist/ai)
7. ✅ **Therapist messages go directly to user**

---

## 🚨 **Important Notes**

### **No Session Reset**

Once a therapist joins (mode = THERAPIST_JOINED), the mode **does NOT reset** automatically. 

- Bot will never respond again in that session
- This is intentional - therapist remains in control
- To re-enable bot, would need manual DB update (not implemented)

### **Multiple Therapists**

Current implementation allows any number of therapists to join:

- First therapist sets mode to THERAPIST_JOINED
- Subsequent therapists can also send messages
- All therapist messages are broadcast to user
- Bot remains silent for all

### **Query Parameter Approach**

Using `?therapist=true` is simple but not secure:

- ✅ Works without authentication
- ✅ Simple to implement
- ⚠️ Anyone with link can join as therapist
- ⚠️ Not suitable for production without proper auth

**For production:** Replace with proper therapist authentication.

---

## 📝 **Files Modified**

### **Backend** (4 files):

1. `backend/app/models/chat_session.py` - New model
2. `backend/app/db/base.py` - Import ChatSession
3. `backend/app/routers/chat.py` - Session mode checking
4. `backend/app/routers/chat.py` - Therapist join endpoint

### **Frontend** (4 files):

1. `frontend/services/api.ts` - therapistJoinSession()
2. `frontend/hooks/useWebSocket.ts` - SYSTEM_MESSAGE handling
3. `frontend/app/chat/[sessionId]/page.tsx` - Therapist detection
4. `frontend/app/therapist/session/[sessionId]/page.tsx` - Query param

---

## 🎯 **Summary**

**The system now intelligently routes chat messages:**

- **User alone** → Bot responds
- **Therapist joins** → System notifies user, bot stops
- **Therapist + User** → Direct communication

**This ensures professional support isn't interrupted by automated responses!**

---

**Last Updated:** January 20, 2026  
**Status:** ✅ **COMPLETE & TESTED**  
**GitHub:** Pushed to main branch
