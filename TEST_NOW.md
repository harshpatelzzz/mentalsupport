# 🧪 TEST ESCALATION NOW - 30 SECONDS

## ⚡ **QUICK TEST (Do This Right Now)**

### 1. Open Chat
```
http://localhost:3000
```
Click "Chat Now"

### 2. Type This EXACT Message
```
i need a therapist
```
Press Enter

### 3. Check Backend Logs
Open another terminal:
```bash
docker-compose logs -f backend
```

### 4. What You Should See

**Backend Logs (MUST show these):**
```
================================================================================
🔍 CHECKING FOR ESCALATION INTENT
Session: [uuid]
Message: 'i need a therapist'
================================================================================

Checking intent for: 'i need a therapist'

================================================================================
🚨🚨🚨 KEYWORD MATCH FOUND 🚨🚨🚨
Keyword: 'therapist'
User message: 'i need a therapist'
================================================================================

🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨
🚨 ESCALATION INTENT DETECTED - STOPPING AI RESPONSE 🚨
🚨 Session: [uuid]
🚨 Message: 'i need a therapist'
🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨

✅ Escalation record created: ID=[uuid]
📤 Broadcasting SYSTEM_SUGGESTION to all connections...
✅ SYSTEM_SUGGESTION broadcast complete
🛑 RETURNING NOW - NO AI RESPONSE WILL BE GENERATED 🛑
```

**Frontend (Browser - Press F12 → Console):**
```
📥 WebSocket message received: SYSTEM_SUGGESTION
🚨 SYSTEM_SUGGESTION received: I understand you'd like to speak with a therapist...
✅ Dispatched escalation-suggestion event
🚨 escalation-suggestion event received!
✅ Escalation UI state updated - should show amber alert
```

**UI (What you see on screen):**
```
┌─────────────────────────────────────────────────┐
│ ⚠️  I understand you'd like to speak with a     │
│     therapist. Would you like me to book an     │
│     appointment for you right away?             │
│                                                  │
│  [✓ Yes, book appointment]  [Not now]           │
└─────────────────────────────────────────────────┘
```
- Text input is HIDDEN
- Only buttons visible
- NO AI response shown

---

## ❌ **IF IT DOESN'T WORK**

### Check 1: Backend Logs Don't Show Intent Detection

**Problem:** No logs with "🚨 KEYWORD MATCH FOUND"

**Solution:**
```bash
# Restart backend
docker-compose restart backend

# Try again with exact phrase
"i need a therapist"
```

### Check 2: AI Response Still Appears

**Problem:** You see an AI response instead of amber alert

**Check Backend Logs For:**
```
💬 GENERATING NORMAL AI RESPONSE
```

**If you see this, it means the `continue` statement didn't work.**

**Solution:**
```bash
# Check if there are syntax errors
docker-compose logs backend | grep -i error

# Restart everything
docker-compose restart backend frontend
```

### Check 3: No Amber Alert on Frontend

**Problem:** Backend logs show escalation, but no UI change

**Check Browser Console (F12):**
- Do you see `📥 WebSocket message received: SYSTEM_SUGGESTION`?

**If NO:**
- WebSocket not connected
- Refresh page and try again

**If YES but no amber alert:**
- Event listener not working
- Restart frontend:
  ```bash
  docker-compose restart frontend
  ```

---

## 🔍 **DEBUGGING COMMANDS**

### View Real-Time Backend Logs
```bash
docker-compose logs -f backend
```

### View Real-Time Frontend Logs
```bash
docker-compose logs -f frontend
```

### Check if Services are Running
```bash
docker-compose ps
```

Should show:
- ✅ neurosupport_backend: Up
- ✅ neurosupport_frontend: Up
- ✅ neurosupport_db: Up (healthy)

### Restart Everything
```bash
docker-compose restart backend frontend
```

---

## ✅ **SUCCESS CHECKLIST**

After typing "i need a therapist":

- [ ] Backend logs show 🚨🚨🚨 KEYWORD MATCH FOUND
- [ ] Backend logs show 🛑 RETURNING NOW - NO AI RESPONSE
- [ ] Backend logs do NOT show 💬 GENERATING NORMAL AI RESPONSE
- [ ] Frontend console shows 📥 WebSocket message received: SYSTEM_SUGGESTION
- [ ] Amber alert box appears on screen
- [ ] Text input is hidden
- [ ] Two buttons visible: "Yes, book appointment" and "Not now"

---

## 🎯 **KEYWORDS THAT TRIGGER ESCALATION**

Try any of these (each will trigger escalation):

✅ `"i need a therapist"`
✅ `"can i talk to a human"`
✅ `"i want a real person"`
✅ `"book an appointment"`
✅ `"i need a professional"`
✅ `"i need a doctor"`
✅ `"i need a counselor"`
✅ `"help me please therapist"`
✅ `"talk to someone"`
✅ `"need help from human"`

---

## 📊 **WHAT'S DIFFERENT NOW**

### Massive Logging
Every step is logged with visual separators:
- `================================================================================`
- `🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨`

You CANNOT miss when escalation triggers.

### Explicit Flow Control
```python
if intent_detected:
    # Create escalation
    # Send SYSTEM_SUGGESTION
    continue  # <-- THIS STOPS AI RESPONSE
```

The `continue` statement jumps back to the start of the while loop, skipping all AI response code.

### More Keywords
Added specific phrases:
- "need a therapist"
- "need therapist"
- "want therapist"
- "see a therapist"
- "talk to therapist"

---

## 🚀 **TEST RIGHT NOW**

1. Open: http://localhost:3000
2. Type: `"i need a therapist"`
3. Watch backend logs in terminal
4. See amber alert appear

**Takes 30 seconds to test!**

---

**Status**: ✅ Enhanced Logging Active
**Test URL**: http://localhost:3000
