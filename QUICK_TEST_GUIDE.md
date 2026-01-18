# 🧪 Quick Test Guide - Fixed Escalation System

## 🎯 Test the Fixes NOW

Your escalation system is **fixed and running**. Here's how to test it:

---

## ⚡ Test 1: Intent Detection (FASTEST TEST)

**This is the easiest way to verify the fix!**

### Steps:
1. Open http://localhost:3000 in your browser
2. Click **"Chat Now"**
3. Type exactly: `"I need a therapist"`
4. Press Enter

### Expected Result ✅:
```
┌────────────────────────────────────────────┐
│ ⚠️  I understand you'd like to speak with  │
│     a therapist. Would you like me to book │
│     an appointment for you right away?     │
│                                             │
│  [✓ Yes, book appointment]  [Not now]      │
└────────────────────────────────────────────┘
```

**What to verify:**
- ⚡ Amber alert appears **INSTANTLY** (no AI response)
- 🚫 Text input field is **HIDDEN**
- ✅ Only buttons visible
- 📝 Placeholder text: "Please respond to the suggestion above"

**If this works, YOUR FIX IS SUCCESSFUL!**

---

## 🔄 Test 2: AI Repetition Detection

### Steps:
1. Start a new chat
2. Send messages that might confuse the AI
3. Watch for repeated AI responses
4. After 3 identical responses, escalation should trigger

### Keywords to try:
```
"Tell me something"
"What should I do"
"I don't understand"
```

### Expected Result ✅:
- After AI repeats same response 3 times
- System detects looping
- Amber alert appears automatically
- Reason logged: "ai_repetition"

---

## 🎫 Test 3: Complete Booking Flow

### Steps:
1. Trigger escalation (any method)
2. Click **"Yes, book appointment"**
3. Wait for confirmation

### Expected Result ✅:
```
┌────────────────────────────────────────────┐
│ ✅ Your appointment has been booked!       │
│    A therapist will join this chat at the  │
│    scheduled time.                         │
└────────────────────────────────────────────┘
```

**What happens:**
1. Button shows loading spinner
2. Backend receives "yes" message
3. Auto-book API creates appointment
4. Green confirmation appears
5. Success message auto-hides after 10 seconds
6. Input re-enabled

**Verify in Therapist Dashboard:**
- Go to http://localhost:3000/therapist
- See your new appointment listed
- Status: "scheduled"
- Time: ~2 hours from now

---

## ❌ Test 4: Decline Flow

### Steps:
1. Trigger escalation
2. Click **"Not now"**

### Expected Result ✅:
- Amber alert disappears
- Text input re-enabled
- Chat continues normally
- Escalation won't trigger again this session

---

## 🔥 Test 5: Keywords That Trigger Intent

Try typing any of these messages:

```
✅ "I need a therapist"
✅ "Can I talk to a human?"
✅ "I want a real person"
✅ "Book an appointment"
✅ "I need someone professional"
✅ "Can I see a doctor?"
✅ "I need a counselor"
✅ "Help me please, I need a therapist"
```

**All should trigger INSTANT escalation!**

---

## 📊 Monitor Backend Logs

Open a terminal and run:
```bash
docker-compose logs -f backend
```

### What to look for:

**Intent Detection:**
```
WARNING - User intent detected: keyword 'therapist' found in message
WARNING - User intent for therapist detected in session {uuid}
```

**AI Repetition:**
```
WARNING - AI repetition detected: same response appeared 3 times
```

**Escalation Triggered:**
```
WARNING - Chat health issue detected in session {uuid}: user_request
```

---

## 🎨 Visual Verification Checklist

When escalation triggers, verify:

- [ ] 🟡 Amber alert box appears
- [ ] ⚠️ Warning icon visible
- [ ] 💬 Clear message text
- [ ] 🔘 Two buttons visible
- [ ] 🚫 Text input HIDDEN (not just disabled)
- [ ] 📝 Placeholder text shows below
- [ ] ⏳ Loading spinner on "Yes" click
- [ ] ✅ Green success after booking
- [ ] ↩️ Input returns after decline

---

## 🐛 Troubleshooting

### Issue: Alert doesn't appear

**Check:**
1. Backend logs for errors
2. WebSocket connection status (should show "Connected")
3. Try exact phrase: "I need a therapist"

**Solution:**
```bash
docker-compose restart backend frontend
```

### Issue: Input still visible

**Check:**
1. Frontend console for errors (F12 → Console)
2. React state updates

**Solution:**
```bash
docker-compose restart frontend
```

### Issue: Booking fails

**Check:**
1. Backend logs: `docker-compose logs backend | grep -i error`
2. Database connection
3. API response in browser console

**Solution:**
```bash
docker-compose restart backend
```

---

## 🎯 Success Criteria

Your system is working correctly if:

1. ✅ Typing "I need a therapist" triggers **instant** escalation
2. ✅ No AI response generated when escalation triggers
3. ✅ Input field is **hidden** during escalation
4. ✅ Clicking "Yes" successfully books appointment
5. ✅ Clicking "Not now" dismisses escalation
6. ✅ Only ONE escalation per session (try triggering again)
7. ✅ Backend logs show correct trigger reasons

---

## 📸 Before/After Comparison

### BEFORE (Broken) ❌
```
User: "I need a therapist"
  ↓
AI: "I'm here to help..."  ← LOOPS
  ↓
User: "No, a REAL therapist"
  ↓
AI: "I'm here to help..."  ← LOOPS AGAIN
  ↓
[Never escalates]
```

### AFTER (Fixed) ✅
```
User: "I need a therapist"
  ↓
⚡ INSTANT ESCALATION
  ↓
[Amber alert shows]
  ↓
User clicks "Yes"
  ↓
✅ Appointment booked!
```

---

## 🚀 Quick Start

**Test right now in 30 seconds:**

1. Open: http://localhost:3000
2. Click: "Chat Now"
3. Type: "I need a therapist"
4. See: Instant amber alert ⚡

**That's it! If this works, everything works!**

---

## 📞 Need Help?

1. Check backend logs: `docker-compose logs -f backend`
2. Check frontend console: F12 → Console tab
3. Restart services: `docker-compose restart backend frontend`
4. Review: `ESCALATION_FIX_SUMMARY.md`

---

**Last Updated:** January 18, 2026  
**Status:** ✅ All Fixes Deployed  
**Test URL:** http://localhost:3000
