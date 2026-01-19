# 🤖 Google Gemini AI Integration - Setup Guide

## ✨ **What This Adds**

The NeuroSupport platform now uses **Google Gemini AI** for intelligent chat responses!

**Key Features:**
- 🧠 **Smart Responses**: Gemini understands context and provides empathetic mental health support
- 🚨 **Auto-Escalation**: Gemini outputs `<<ESCALATE>>` token when users need therapist help
- 💬 **Natural Conversations**: No more robotic rule-based responses
- 🔄 **Fallback Support**: Works without API key (uses simple responses)

---

## 🎯 **How It Works**

### 1. System Prompt

Gemini is configured with this special prompt:

```
You are a mental health support assistant.

Rules you MUST follow:
- Be empathetic and human
- Never repeat the same question twice
- If the user asks for a therapist, appointment, or human help:
  respond ONLY with the word: <<ESCALATE>>
- If the user seems distressed or stuck:
  suggest speaking to a therapist gently
- Do NOT give medical advice
- Keep responses short and supportive (2-3 sentences max)
```

### 2. Escalation Flow

```
User: "I need a therapist"
  ↓
Gemini: "<<ESCALATE>>"
  ↓
Backend detects <<ESCALATE>> token
  ↓
Creates escalation record
  ↓
Sends SYSTEM_SUGGESTION
  ↓
Frontend shows booking buttons
```

### 3. Three Escalation Paths

**Path 1: Keyword Shortcut** (Fastest)
- User message contains: "therapist", "appointment", etc.
- Immediate escalation before calling Gemini

**Path 2: Gemini Detection** (Smartest)
- Gemini analyzes user's message
- Gemini outputs <<ESCALATE>>
- Backend triggers escalation

**Path 3: Chat Health** (Fallback)
- AI loops 3+ times
- 3+ negative emotions detected
- Escalation triggered

---

## 🔑 **Setup Instructions**

### Option 1: With Gemini AI (Recommended)

#### Step 1: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Create new key or use existing
4. Copy the API key

#### Step 2: Set Environment Variable

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Docker Compose (Recommended):**

Edit `docker-compose.yml`:

```yaml
backend:
  environment:
    - GEMINI_API_KEY=your-api-key-here  # Add this line
    - USE_GEMINI=true                    # Enable Gemini
```

**Or create `.env` file:**

```bash
# .env
GEMINI_API_KEY=your-api-key-here
USE_GEMINI=true
```

#### Step 3: Restart Backend

```bash
docker-compose restart backend
```

#### Step 4: Verify

Check backend logs:

```bash
docker-compose logs backend | grep -i gemini
```

Should see:
```
✅ Gemini AI initialized successfully
```

---

### Option 2: Without Gemini AI (Fallback)

The system works fine without Gemini! It uses simple rule-based responses.

**No setup needed** - just leave `GEMINI_API_KEY` empty.

Backend will log:
```
GEMINI_API_KEY not set - using fallback responses
```

**Note:** Keyword-based escalation still works perfectly!

---

## 🧪 **Testing**

### Test 1: Simple Escalation Request

**With Gemini:**
```
User: "I need to talk to a therapist"
Gemini: "<<ESCALATE>>"
System: [Shows booking buttons]
```

**Without Gemini:**
```
User: "I need to talk to a therapist"
Keyword Detection: "therapist" found
System: [Shows booking buttons]
```

Both work!

### Test 2: Natural Language Understanding

**With Gemini (Better):**
```
User: "Nothing is helping me anymore"
Gemini: "I'm sorry you're feeling this way. It sounds like you might benefit from professional support. Would you like to speak with a therapist?"
```

**Without Gemini (Basic):**
```
User: "Nothing is helping me anymore"
System: "I hear you. Can you tell me more about how you're feeling?"
```

### Test 3: Escalation Detection

**With Gemini (Smarter):**
```
User: "Can I schedule a session with someone?"
Gemini: "<<ESCALATE>>"
System: [Triggers booking flow]
```

**Without Gemini:**
```
User: "Can I schedule a session with someone?"
Keyword: "schedule" detected
System: [Triggers booking flow]
```

---

## 📊 **Backend Logs to Watch**

### Successful Gemini Initialization

```
INFO - Using rule-based emotion detection for fast startup
INFO - ✅ Gemini AI initialized successfully
INFO - Starting NeuroSupport application...
```

### Gemini Response Generation

```
INFO - Sending to Gemini:
User: I'm feeling sad
INFO - Gemini response: I'm here for you. It's okay to feel sad...
```

### Gemini Escalation Detection

```
WARNING - ================================================================================
WARNING - 🚨 GEMINI AI DETECTED ESCALATION NEED 🚨
WARNING - Session: [uuid]
WARNING - Gemini said: <<ESCALATE>>
WARNING - ================================================================================
WARNING - ✅ Created Gemini escalation record ID: [uuid]
WARNING - 📤 Sending SYSTEM_SUGGESTION (Gemini escalation)
WARNING - 🛑 SKIPPING AI RESPONSE - Gemini triggered escalation
```

---

## 🔧 **Configuration Options**

### In `backend/app/core/config.py`:

```python
# Gemini AI Configuration
GEMINI_API_KEY: str = ""        # Your API key
USE_GEMINI: bool = False         # Enable/disable Gemini
```

### Runtime Toggle

You can disable Gemini without removing the API key:

```yaml
# docker-compose.yml
environment:
  - GEMINI_API_KEY=your-key
  - USE_GEMINI=false  # Temporarily disable
```

---

## 🚨 **Troubleshooting**

### Issue: "google.generativeai not found"

**Solution:**
```bash
# Rebuild backend container
docker-compose build backend
docker-compose up -d backend
```

### Issue: "GEMINI_API_KEY not set"

**Check:**
```bash
docker-compose exec backend env | grep GEMINI
```

**Should show:**
```
GEMINI_API_KEY=your-api-key-here
USE_GEMINI=true
```

**Fix:**
```bash
# Edit docker-compose.yml
# Add GEMINI_API_KEY to backend environment
docker-compose restart backend
```

### Issue: Gemini responses too slow

**Note:** First request is slower (model initialization)

**Solution:** Keep container running (don't restart frequently)

### Issue: API quota exceeded

**Gemini Free Tier:**
- 60 requests per minute
- Should be enough for testing

**Solution:** Wait 1 minute or upgrade plan

---

## 💰 **Cost Analysis**

### Gemini Pro API Pricing (as of 2024)

**Free Tier:**
- 60 requests/minute
- Perfect for development

**Paid Tier:**
- $0.00025 per 1K characters (input)
- $0.0005 per 1K characters (output)

**Example:**
- 100 conversations/day
- Average 10 messages each
- ~50 characters per message
= **~$0.01/day** ($0.30/month)

**Very affordable!**

---

## 🎓 **How the Integration Works**

### 1. `gemini_service.py`

```python
class GeminiService:
    SYSTEM_PROMPT = "You are a mental health support assistant..."
    
    def generate_response(self, conversation_history):
        # Format history
        # Call Gemini API
        # Return response (may contain <<ESCALATE>>)
```

### 2. `chat_service.py`

```python
def get_ai_response(message, session_id, db):
    # Build conversation history
    # Call Gemini service
    # Return AI response
```

### 3. `chat.py` (WebSocket Handler)

```python
# Generate AI response
ai_response = chat_service.get_ai_response(message, session_id, db)

# Check for escalation token
if "<<ESCALATE>>" in ai_response:
    # Trigger escalation
    # Send SYSTEM_SUGGESTION
    # Skip showing <<ESCALATE>> to user
```

---

## ✅ **Benefits**

### With Gemini AI:
- ✅ Natural conversations
- ✅ Context awareness
- ✅ Intelligent escalation detection
- ✅ No response loops
- ✅ Empathetic responses
- ✅ Better user experience

### Without Gemini AI:
- ✅ Still works perfectly
- ✅ Fast responses
- ✅ No API costs
- ✅ Keyword escalation works
- ✅ No external dependencies

---

## 🎯 **Quick Start**

1. **Get API key**: https://makersuite.google.com/app/apikey
2. **Edit `docker-compose.yml`**:
   ```yaml
   backend:
     environment:
       - GEMINI_API_KEY=your-key-here
       - USE_GEMINI=true
   ```
3. **Restart**:
   ```bash
   docker-compose restart backend
   ```
4. **Test**:
   - Open http://localhost:3000
   - Type: "I need a therapist"
   - See instant escalation!

---

## 📞 **Support**

- **Gemini Documentation**: https://ai.google.dev/docs
- **API Key Management**: https://makersuite.google.com/app/apikey
- **Pricing**: https://ai.google.dev/pricing

---

**Last Updated**: January 18, 2026  
**Status**: ✅ Integrated and Working  
**Works Without API Key**: ✅ Yes (fallback mode)
