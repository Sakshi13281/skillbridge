# SkillBridge 🎯

An AI-powered skill gap analyzer that helps you understand exactly what skills you need to land your dream job — and builds a personalised learning roadmap to get you there.

---

## What it does

SkillBridge uses **Groq AI (Llama 3)** to analyse your skills against real job requirements. Unlike traditional skill trackers that use hardcoded data, SkillBridge sends your skill ratings to an AI model that thinks like a real hiring manager — explaining *why* each skill matters and predicting your actual hiring chances.

**Core features:**

- 🔍 **Skill Gap Analysis** — rate your skills and get AI-powered gap analysis for any tech role
- 📄 **Resume Upload** — upload your PDF resume and AI extracts your skills automatically
- 🎯 **Hiring Chance Prediction** — get a realistic % chance of getting hired right now
- 🗺️ **Personalised Roadmap** — week-by-week learning plan with real resources to close every gap
- 📊 **Dashboard** — track your progress, scores, and analysis history
- 🔐 **Authentication** — secure login and registration with JWT tokens

---

## Tech Stack

**Frontend**
- HTML, CSS, JavaScript
- Google Fonts (Syne + DM Sans)
- Live Server (development)

**Backend**
- Python 3.11+
- FastAPI
- SQLite + aiosqlite
- JWT authentication (python-jose)
- Password hashing (bcrypt + passlib)

**AI**
- Groq API (Llama 3.3 70B) for skill analysis, hiring prediction and roadmap generation
- PyPDF2 for resume text extraction

---

## Project Structure

```
skillbridge/
├── frontend/
│   ├── index.html          # Homepage with job role cards
│   ├── analyzer.html       # Skill rating + resume upload
│   ├── results.html        # Gap analysis + hiring prediction
│   ├── roadmap.html        # Week-by-week learning plan
│   ├── dashboard.html      # Stats and history
│   ├── login.html          # Sign in and register
│   ├── profile.html        # User profile
│   ├── style.css           # Shared styles
│   └── api.js              # All backend API calls
│
└── backend/
    ├── main.py             # FastAPI app entry point
    ├── database.py         # SQLite setup
    ├── auth.py             # JWT + password hashing
    ├── gemini.py           # Groq AI integration
    ├── requirements.txt
    ├── .env.example
    └── routers/
        ├── auth.py         # Register, login, me
        ├── skills.py       # Job roles and skills
        ├── analysis.py     # AI skill gap analysis
        ├── roadmap.py      # AI roadmap generation
        ├── resume.py       # PDF resume upload + extraction
        ├── dashboard.py    # User stats
        └── profile.py      # Profile management
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- A free Groq API key from [console.groq.com](https://console.groq.com)
- VS Code with Live Server extension

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/Sakshi13281/skillbridge.git
cd skillbridge
```

**2. Create and activate virtual environment:**
```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Mac/Linux
source .venv/bin/activate
```

**3. Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

**4. Set up environment variables:**
```bash
copy .env.example .env
```

Open `.env` and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=skillbridge-secret-key-2024
```

**5. Start the backend:**
```bash
uvicorn main:app --reload
```

You should see:
```
✅ Database ready!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**6. Open the frontend:**

Right-click `frontend/index.html` in VS Code → **Open with Live Server**

The app will open at `http://127.0.0.1:5500`

---

## How to Use

1. **Create an account** on the login page
2. **Pick a job role** from the homepage — Data Analyst, Frontend Developer etc
3. **Rate your skills** using sliders — or upload your PDF resume for AI extraction
4. **View your results** — readiness score, skill gaps, and hiring chance prediction
5. **Generate your roadmap** — get a week-by-week learning plan
6. **Track progress** on the dashboard as you complete roadmap tasks

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new account |
| POST | `/auth/login` | Login and get token |
| GET | `/skills/roles` | Get all job roles |
| GET | `/skills/roles/{id}/skills` | Get skills for a role |
| POST | `/analysis/run` | Run AI skill gap analysis |
| GET | `/analysis/latest` | Get latest analysis |
| POST | `/roadmap/generate` | Generate AI learning roadmap |
| GET | `/roadmap/latest` | Get latest roadmap |
| PATCH | `/roadmap/task/{id}/complete` | Toggle task completion |
| POST | `/resume/extract` | Extract skills from PDF resume |
| GET | `/dashboard/stats` | Get user stats |
| GET | `/profile/` | Get user profile |
| PUT | `/profile/update` | Update profile |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key from console.groq.com |
| `SECRET_KEY` | Secret key for JWT token signing |

---

## Screenshots

> Homepage with job role cards

> Results page with AI analysis and hiring prediction

> Week-by-week learning roadmap

---

## Future Features

- [ ] Role comparison — compare two job roles side by side
- [ ] AI chat mentor — ask career questions directly
- [ ] Progress tracking — visualise score improvement over time
- [ ] Email notifications — weekly roadmap reminders
- [ ] Mobile responsive improvements
- [ ] Cloud deployment

---

## License

MIT License — feel free to use this project for learning or as a portfolio piece.

---

Built with ❤️ using FastAPI, Groq AI, and vanilla JavaScript.
