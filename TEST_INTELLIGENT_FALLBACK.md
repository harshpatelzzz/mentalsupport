# 🧪 Test Guide: Intelligent Fallback Feature

## Quick Start

Your NeuroSupport platform is **running** with the new intelligent fallback feature.

**Access Points:**
- Homepage: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Therapist Dashboard: http://localhost:3000/therapist

---

## 🎮 Step-by-Step Testing

### Test Scenario: Emotional Distress Detection

This is the easiest way to trigger the escalation feature.

#### Step 1: Start a New Chat

1. Open http://localhost:3000 in your browser
2. Click the big **"Chat Now"** button
3. Optional: Enter a name or leave blank
4. Click "Start Chatting"

#### Step 2: Send Messages with Negative Emotions

Type these messages one by one (wait for AI response between each):

```
Message 1: "I'm feeling really sad today"
[Wait for AI response]

Message 2: "I'm also very anxious about everything"
[Wait for AI response]

Message 3: "I feel so depressed and hopeless"
[Wait for AI response]

Message 4: "Nothing seems to help me"
[Wait for AI response]
```

#### Step 3: Watch for Escalation

After 3-4 messages with negative emotions (sad, anxious, depressed), you should see:

**🎨 Amber Alert Box Appears:**

```
┌─────────────────────────────────────────────────────┐
│  ⚠️  I want to make sure you get the best support.  │
│      It might help to talk with a professional       │
│      therapist. Would you like me to book an         │
│      appointment for you?                            │
│                                                       │
│      [✓ Yes, book appointment]  [Not now]            │
└─────────────────────────────────────────────────────┘
```

#### Step 4: Accept Appointment Booking

1. Click **"Yes, book appointment"** button
2. You'll see a loading spinner briefly
3. Backend auto-books appointment for 2 hours from now

#### Step 5: See Confirmation

**🎨 Green Success Box Appears:**

```
┌─────────────────────────────────────────────────────┐
│  ✅ Your appointment has been booked!                │
│      A therapist will join this chat at the          │
│      scheduled time.                                 │
└─────────────────────────────────────────────────────┘
```

#### Step 6: Verify in Therapist Dashboard

1. Open http://localhost:3000/therapist in a new tab
2. You should see your newly created appointment
3. Status: "scheduled"
4. Time: ~2 hours from current time

---

## 🔍 What to Look For

### Backend Logs (Terminal)

Run this to watch backend activity:
```bash
docker-compose logs -f backend
```

**Expected log entries:**

```
INFO - Detected negative emotion: sadness
INFO - Detected negative emotion: fear
WARNING - Chat health check: Emotional distress detected (3 negative emotions)
WARNING - Triggering escalation for session {uuid}: emotional_distress
INFO - Auto-booked appointment {uuid} for session {uuid}
```

### Frontend Behavior

✅ **Before Escalation:**
- Normal chat interface
- Messages with emotion badges
- AI responds to each message

✅ **During Escalation:**
- Amber alert box slides in smoothly
- Input field placeholder changes
- Buttons are clearly visible
- Message history still scrollable

✅ **After Acceptance:**
- Loading spinner shows during API call
- Amber alert disappears
- Green confirmation appears
- Chat continues normally
- Can still send messages

✅ **After Decline:**
- Alert disappears immediately
- Chat continues normally
- Won't trigger again for this session

---

## 🧪 Alternative Test Scenarios

### Test 2: Decline Escalation

Follow Steps 1-3 above, then:

1. When amber alert appears
2. Click **"Not now"** button
3. Alert disappears
4. Continue chatting normally
5. Escalation won't trigger again

### Test 3: Multiple Sessions

1. Complete Test 1 (accept booking)
2. Start a **new chat session** (new visitor)
3. Trigger escalation again
4. Verify it works for new session too
5. Check therapist dashboard shows both

### Test 4: View Escalations (API)

Open http://localhost:8000/docs in browser:

1. Scroll to **"therapist"** section
2. Find `GET /api/therapist/escalations`
3. Click "Try it out"
4. Click "Execute"
5. See all escalation records

**Or use browser:**
```
http://localhost:8000/api/therapist/escalations
```

### Test 5: Therapist Joins Escalated Session

1. After booking appointment via escalation
2. Open http://localhost:3000/therapist
3. Find the appointment in list
4. Click **"Join Chat"**
5. You're now in the same chat as visitor
6. Send message as therapist
7. Both sides see messages in real-time

---

## 🐛 Troubleshooting

### Issue: Alert Doesn't Appear

**Possible Causes:**
- Not enough messages sent (need 3-4)
- Emotions not detected (keywords not matched)
- Already triggered in this session

**Solution:**
- Start a new chat session
- Use exact phrases from Step 2
- Check backend logs for emotion detection

### Issue: Booking Fails

**Possible Causes:**
- Backend not running
- Database connection issue
- Network error

**Solution:**
```bash
# Check services
docker-compose ps

# Restart if needed
docker-compose restart backend

# Check logs
docker-compose logs backend
```

### Issue: Alert Appears Immediately

**Possible Cause:**
- Threshold too sensitive

**Solution:**
- Adjust thresholds in `chat_health_service.py`
- Restart backend: `docker-compose restart backend`

---

## 📊 Verification Checklist

After testing, verify:

- [ ] Amber alert appeared after 3-4 sad messages
- [ ] Buttons are clickable and responsive
- [ ] Loading spinner shows during booking
- [ ] Green confirmation appears after booking
- [ ] Appointment visible in therapist dashboard
- [ ] Backend logs show escalation trigger
- [ ] Only triggered once per session
- [ ] Decline button works
- [ ] Chat continues after accept/decline
- [ ] No errors in console or logs

---

## 🎯 Success Indicators

### You'll know it's working when:

1. **Detection Works**
   - Backend logs show: "Chat health check: Emotional distress detected"
   - Escalation record created in database

2. **UI Updates**
   - Amber box appears smoothly
   - No page flicker or reload
   - Buttons are styled correctly

3. **Booking Works**
   - API call succeeds
   - Appointment created in database
   - Visible in therapist dashboard

4. **Confirmation Shows**
   - Green success box appears
   - Message is clear and reassuring
   - User can continue chatting

---

## 📸 Visual Guide

### Normal Chat Flow
```
┌─────────────────────────────────┐
│ Support Chat         [Connected] │
├─────────────────────────────────┤
│                                  │
│  You: I'm feeling sad            │
│  [sadness 75%]                   │
│                                  │
│      AI: I'm sorry you're        │
│      feeling this way...         │
│                                  │
│  You: I'm also anxious           │
│  [fear 80%]                      │
│                                  │
│      AI: Let's take this         │
│      one step at a time...       │
│                                  │
│  You: Nothing helps              │
│  [sadness 85%]                   │
│                                  │
│      AI: I hear you...           │
│                                  │
├─────────────────────────────────┤
│  Type your message... [Send]     │
└─────────────────────────────────┘
```

### After Escalation Triggers
```
┌─────────────────────────────────┐
│ Support Chat         [Connected] │
├─────────────────────────────────┤
│                                  │
│  [Previous messages...]          │
│                                  │
├─────────────────────────────────┤
│ ⚠️ SYSTEM MESSAGE                │
│                                  │
│  I want to make sure you get     │
│  the best support. It might      │
│  help to talk with a             │
│  professional therapist. Would   │
│  you like me to book an          │
│  appointment for you?            │
│                                  │
│  [✓ Yes, book]  [Not now]        │
├─────────────────────────────────┤
│  Please respond above... [Send]  │
└─────────────────────────────────┘
```

### After Booking Confirmed
```
┌─────────────────────────────────┐
│ Support Chat         [Connected] │
├─────────────────────────────────┤
│                                  │
│  [Previous messages...]          │
│                                  │
├─────────────────────────────────┤
│ ✅ SUCCESS                        │
│                                  │
│  Your appointment has been       │
│  booked! A therapist will join   │
│  this chat at the scheduled      │
│  time.                           │
├─────────────────────────────────┤
│  Type your message... [Send]     │
└─────────────────────────────────┘
```

---

## 🎊 Enjoy Testing!

This feature demonstrates sophisticated AI + human collaboration in mental health support.

**Remember:** The system is designed to be helpful, not pushy. Users maintain full control over their experience.

**Questions or Issues?**
- Check backend logs: `docker-compose logs -f backend`
- Check API docs: http://localhost:8000/docs
- Review documentation files in project root

**Happy Testing!** 🚀
