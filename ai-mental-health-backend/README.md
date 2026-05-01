# 🧠 AI Mental Health Backend

A production-grade REST API for mental health support — powered by **Groq (LLaMA 3.3 70B)** and **Firebase Firestore**.

Built with Flask · Groq AI · Firebase · Python 3.13

---

## 🚀 Features

- 💬 **AI Chat** — CBT-style mental health support via LLaMA 3.3 70B
- 🆘 **Crisis Detection** — auto-detects crisis language and returns helpline info
- 📊 **Mood Tracking** — log, filter, and analyze mood history
- 💡 **Smart Suggestions** — 48 CBT-inspired wellness tips across 11 moods
- 🔥 **Firebase Firestore** — persistent storage for chats and moods
- ❤️ **Health Monitoring** — uptime, dependency checks, liveness probe
- 🛡️ **Input Validation** — every field sanitized and validated
- ⚡ **Fast** — Groq inference typically under 1 second

---

## 📁 Project Structure

```
ai-mental-health-backend/
│
├── app.py                        ← Flask entry point
├── requirements.txt              ← Dependencies
├── Procfile                      ← Render/Railway deployment
├── .env.example                  ← Environment variable template
├── serviceAccountKey.json        ← Firebase credentials (never commit)
│
├── routes/
│   ├── health.py                 ← GET /api/health, /ping, /version
│   ├── chat.py                   ← POST /api/chat
│   ├── mood.py                   ← POST /api/mood, GET /api/mood/history, /summary
│   └── suggestions.py            ← GET /api/suggestions, /all, /moods
│
├── services/
│   ├── gemini_service.py         ← Groq AI client + crisis detection
│   ├── firebase_service.py       ← Firestore singleton client
│   └── suggestions_service.py    ← Mood-to-tip engine
│
└── utils/
    └── validators.py             ← Input validation layer
```

---

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone https://github.com/your-username/ai-mental-health-backend.git
cd ai-mental-health-backend

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

### 2. Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
GROQ_API_KEY=your_groq_api_key_here
FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json
```

Get your keys:
- **Groq API Key** → https://console.groq.com → API Keys → Create Key
- **Firebase Key** → https://console.firebase.google.com → Project Settings → Service Accounts → Generate new private key → rename to `serviceAccountKey.json`

### 3. Run

```bash
python app.py
```

Server starts at → `http://127.0.0.1:5000`

---

## ✅ Testing All Endpoints

Open a second PowerShell tab and run these one by one:

### 🏓 Ping (liveness)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/ping" -Method GET
```

### ❤️ Health Check
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/health" -Method GET
```

### 🔢 Version
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/version" -Method GET
```

### 💬 Chat
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"user_id": "user123", "message": "I feel really anxious today"}'
```

### 📝 Save Mood
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/mood" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"user_id": "user123", "mood": "anxious", "note": "hackathon stress", "intensity": 7}'
```

### 📜 Mood History
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/mood/history?user_id=user123" -Method GET
```

### 📊 Mood Summary
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/mood/summary?user_id=user123" -Method GET
```

### 💡 Get Suggestion
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/suggestions?mood=anxious" -Method GET
```

### 📚 All Suggestions
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/suggestions/all" -Method GET
```

### 🎭 Supported Moods
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/suggestions/moods" -Method GET
```

---

## 🔌 API Reference

### Base URL
```
http://127.0.0.1:5000/api
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ping` | Liveness probe |
| GET | `/health` | Full health + dependency status |
| GET | `/version` | Service version info |
| POST | `/chat` | AI mental health chat |
| POST | `/mood` | Save mood entry |
| GET | `/mood/history` | Get mood history |
| GET | `/mood/summary` | Get mood analytics |
| GET | `/suggestions` | Get wellness tip by mood |
| GET | `/suggestions/all` | Get all tips for all moods |
| GET | `/suggestions/moods` | Get supported mood list |

---

### POST `/api/chat`

**Request:**
```json
{
  "user_id": "user123",
  "message": "I feel really anxious today",
  "mood": "anxious"
}
```

**Response:**
```json
{
  "reply": "It sounds like you're carrying a lot right now...",
  "user_id": "user123",
  "timestamp": "2026-04-30T18:00:00+00:00"
}
```

---

### POST `/api/mood`

**Request:**
```json
{
  "user_id": "user123",
  "mood": "anxious",
  "note": "big presentation today",
  "intensity": 7
}
```

**Response:**
```json
{
  "success": true,
  "message": "Mood logged successfully.",
  "data": {
    "id": "abc123",
    "mood": "anxious",
    "note": "big presentation today",
    "intensity": 7,
    "timestamp": "2026-04-30T18:00:00+00:00"
  }
}
```

---

### GET `/api/mood/summary?user_id=user123`

**Response:**
```json
{
  "user_id": "user123",
  "total_entries": 12,
  "most_common_mood": "anxious",
  "latest_mood": "calm",
  "breakdown": {
    "anxious": 5,
    "sad": 3,
    "calm": 4
  }
}
```

---

### GET `/api/health`

**Response (healthy):**
```json
{
  "service": "ai-mental-health-backend",
  "status": "healthy",
  "version": "1.0.0",
  "uptime": "2h 14m 33s",
  "uptime_seconds": 8073,
  "timestamp": "2026-04-30T18:00:00+00:00",
  "started_at": "2026-04-30T15:45:27+00:00",
  "services": {
    "firebase": { "status": "connected" },
    "groq": { "status": "configured", "model": "llama-3.3-70b-versatile" }
  },
  "system": {
    "python_version": "3.13.0",
    "platform": "Windows",
    "environment": "development"
  }
}
```

---

## 🛡️ Supported Moods

`happy` `sad` `anxious` `angry` `stressed` `tired` `lonely` `overwhelmed` `depressed` `calm` `neutral`

---

## 🆘 Crisis Detection

If a user's message contains crisis-level language (suicidal ideation, self-harm), the system **bypasses the AI entirely** and returns an immediate crisis response with real helpline information. No API call is made — response is instant.

**Detected keywords include:** suicide, self-harm, hurt myself, want to die, and similar phrases.

**Crisis response includes:** Pakistan's Umang helpline (0317-4288665) and encouragement to reach out to a trusted person.

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Flask 3.0 |
| AI Model | LLaMA 3.3 70B via Groq |
| Database | Firebase Firestore |
| Auth | Firebase Admin SDK |
| Validation | Custom validators |
| Deployment | Render / Railway |

---

## 📦 Requirements

```
flask==3.0.3
flask-cors==4.0.1
firebase-admin==6.5.0
python-dotenv==1.0.1
gunicorn==22.0.0
groq>=1.2.0
```

---

## 🚀 Deployment

### Render / Railway

1. Push to GitHub
2. Connect repo to Render or Railway
3. Set environment variables in the dashboard:
   - `GROQ_API_KEY`
   - `FIREBASE_CREDENTIALS_PATH`
4. Start command: `gunicorn app:app`

---

## 👨‍💻 Author

Built for a hackathon by **Muneeb** — backend & API integration.

---

> *This backend is not a substitute for professional mental health care.*