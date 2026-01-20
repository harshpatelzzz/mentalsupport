# 🚀 Quick Start with Gemini AI

## Before You Start

**Current Status:** Gemini is DISABLED (fallback mode)
- Keyword escalation ✅ working
- Simple AI responses ✅ working
- Smart AI responses ❌ not available yet

**After Gemini:** Everything above + context-aware AI conversations!

---

## 🔑 Step 1: Get Free API Key

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIzaSy...`)

**Free tier:** 60 requests/minute (plenty for testing!)

---

## ⚙️ Step 2: Add to docker-compose.yml

Open `docker-compose.yml` in your editor.

Find this section (around line 30):

```yaml
backend:
  environment:
    DATABASE_URL: postgresql://neurosupport:neurosupport123@postgres:5432/neurosupport_db
    FRONTEND_URL: http://localhost:3000
    BACKEND_URL: http://localhost:8000
    DEBUG: "true"
    GEMINI_API_KEY: ""  # 👈 PASTE YOUR KEY HERE
    USE_GEMINI: "false"  # 👈 CHANGE TO "true"
```

**Change to:**

```yaml
backend:
  environment:
    DATABASE_URL: postgresql://neurosupport:neurosupport123@postgres:5432/neurosupport_db
    FRONTEND_URL: http://localhost:3000
    BACKEND_URL: http://localhost:8000
    DEBUG: "true"
    GEMINI_API_KEY: "AIzaSyC_YOUR_KEY_HERE"  # 👈 YOUR KEY
    USE_GEMINI: "true"  # 👈 NOW ENABLED
```

**Save the file!**

---

## 🔄 Step 3: Restart Backend

Run this command:

```bash
docker-compose restart backend
```

Wait ~10 seconds for restart.

---

## ✅ Step 4: Verify Gemini is Working

Check backend logs:

```bash
docker-compose logs backend | grep -i gemini
```

**You should see:**

```
✅ Gemini AI initialized successfully
```

**If you see this, GEMINI IS WORKING! 🎉**

---

## 🧪 Step 5: Test It

### Test 1: Smart Context Understanding

1. Open http://localhost:3000
2. Click "Chat Now"
3. Try this conversation:

```
You: "I've been struggling with sleep"
AI: [Gemini responds with empathy]

You: "Nothing is working anymore"
AI: "<<ESCALATE>>" (or suggests therapist)
   → Triggers appointment booking
```

### Test 2: Natural Escalation

Type any of these:

```
"Can I talk to someone about this?"
"I think I need professional help"
"Is there someone I can speak to?"
```

Gemini will detect the need and output `<<ESCALATE>>`!

---

## 🆚 Before vs After Gemini

### WITHOUT Gemini (Current - Fallback Mode):

```
User: "I'm really struggling"
AI: "I hear you. Can you tell me more?"
```

Simple rule-based response.

### WITH Gemini (Smart Mode):

```
User: "I'm really struggling"
AI: "I'm sorry you're going through this. It sounds like you're dealing with 
     a lot right now. Would you like to talk about what's been most difficult?"
```

Context-aware, empathetic, natural!

---

## 🔍 Troubleshooting

### Issue: "GEMINI_API_KEY not set"

**Check:**
```bash
docker-compose exec backend env | grep GEMINI
```

**Should show:**
```
GEMINI_API_KEY=AIzaSyC...
USE_GEMINI=true
```

**If empty:** You forgot to add the key to docker-compose.yml

**Fix:**
1. Edit docker-compose.yml
2. Add your API key
3. Run: `docker-compose restart backend`

---

### Issue: "API key invalid"

**Reasons:**
- Wrong key copied
- Extra spaces in the key
- Quotes missing

**Fix:**
```yaml
# ❌ WRONG
GEMINI_API_KEY: AIzaSyC...  # Missing quotes

# ❌ WRONG
GEMINI_API_KEY: "AIzaSyC... "  # Extra space at end

# ✅ CORRECT
GEMINI_API_KEY: "AIzaSyC_exact_key_no_spaces"
```

---

### Issue: Still seeing "Gemini AI is disabled"

**Check USE_GEMINI:**
```yaml
# ❌ WRONG
USE_GEMINI: "false"

# ✅ CORRECT
USE_GEMINI: "true"
```

**Save and restart:**
```bash
docker-compose restart backend
```

---

## 📊 What Changes With Gemini?

### Escalation Detection:

**Before (Keyword Only):**
- ✅ "I need a therapist" → Escalates
- ❌ "I think I should talk to someone professional" → No escalation

**After (Gemini Enabled):**
- ✅ "I need a therapist" → Escalates (keyword)
- ✅ "I think I should talk to someone professional" → Escalates (Gemini)
- ✅ "Nothing is helping anymore" → Escalates (Gemini detects distress)

### Conversation Quality:

**Before:**
```
User: "Work is overwhelming"
AI: "I hear you. Can you tell me more?"

User: "I can't sleep anymore"
AI: "I hear you. Can you tell me more?"
```

**After:**
```
User: "Work is overwhelming"
AI: "Work stress can be really difficult. What's been the most challenging part?"

User: "I can't sleep anymore"
AI: "Sleep problems can make everything harder. How long has this been going on?"
```

---

## 💰 Cost

**Free Tier:**
- 60 requests per minute
- 1,500 requests per day
- **Perfect for development!**

**Example usage:**
- 100 chat conversations/day
- 10 messages each
- = 1,000 requests/day
- **Still within free tier! ✅**

**Paid Tier (if you exceed):**
- ~$0.01 per day for typical usage
- ~$0.30 per month

**Extremely cheap!**

---

## 🎯 Quick Reference

### Enable Gemini:
1. Get key: https://aistudio.google.com/app/apikey
2. Edit `docker-compose.yml`
3. Add key to `GEMINI_API_KEY`
4. Set `USE_GEMINI: "true"`
5. Restart: `docker-compose restart backend`

### Verify:
```bash
docker-compose logs backend | grep -i gemini
```

### Disable Gemini:
```yaml
USE_GEMINI: "false"
```

### Test:
http://localhost:3000 → "Chat Now" → Try conversations!

---

## ✅ Success Checklist

After enabling Gemini, confirm:

- [ ] API key added to docker-compose.yml
- [ ] USE_GEMINI set to "true"
- [ ] Backend restarted
- [ ] Logs show "✅ Gemini AI initialized successfully"
- [ ] Chat responses are more natural
- [ ] Escalation still works
- [ ] No errors in logs

---

**Last Updated:** January 20, 2026  
**Gemini Status:** Ready to enable!  
**Cost:** FREE (60 req/min)
