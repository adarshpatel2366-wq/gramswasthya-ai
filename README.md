# GramSwasthya AI 🩺

AI Healthcare Assistant for rural India — chat guidance, report/prescription
explanation, nearby hospital finder, multilingual (Hindi / English / Hinglish),
voice input/output, and an admin dashboard.

## Stack

- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **Backend:** FastAPI (Python)
- **Database:** SQLite by default (dev) → PostgreSQL in production
- **AI:** Groq API, `llama-3.3-70b-versatile`
- **Maps:** OpenStreetMap Overpass + Nominatim (free, no key needed) — swap for Google Maps API for richer data
- **Auth:** JWT, email/password + OTP scaffold + Google login scaffold

## What's fully built vs. stubbed

**Fully working:**
- Signup / login / JWT auth, protected routes
- AI chat with conversation memory, Hindi/English/Hinglish auto-detection, emergency detection (rule-based + AI), conversation history, per-conversation AI summary
- Nearby hospital/PHC/pharmacy search via OpenStreetMap (no API key required)
- File upload endpoint (reports/prescriptions/skin images) with local storage + AI summary hook
- Admin stats/users/feedback/error-log endpoints
- Dark mode, voice input (Web Speech API), voice output, markdown chat rendering, responsive UI

**Stubbed — intentionally left as clear TODOs, since they need your own credentials/infra:**
- OTP SMS delivery (currently logs OTP to console — plug in MSG91/Twilio)
- Google Login token verification (`app/routers/auth.py` → `/google`)
- OCR of uploaded PDFs/images before AI summarization (currently sends placeholder text — plug in `pytesseract` or a cloud OCR API)
- Cloudinary upload (falls back to local disk storage until credentials are set)
- Chat PDF export (`jspdf` is included in package.json — a few lines in `chat/page.tsx` will wire it up)
- Medicine reminders / appointment notes (schema-ready, no endpoints yet)

This is a real, running foundation — not a mockup — built to be extended quickly rather than
a finished, audited production system. Treat the security/auth pieces as a strong starting
point and get a security review before handling real patient data at scale.

## Local setup

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set GROQ_API_KEY at minimum
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Visit `http://localhost:3000`. The Next.js dev server proxies `/api/*` to the FastAPI
backend on port 8000 (see `next.config.js`).

## Getting a Groq API key
Sign up at https://console.groq.com, create an API key, and put it in `backend/.env`
as `GROQ_API_KEY`.

## Deployment

- **Frontend → Vercel:** import the `frontend/` folder as the project root, set
  `NEXT_PUBLIC_API_URL` to your deployed backend URL.
- **Backend → Render/Railway:** deploy `backend/`, set env vars from `.env.example`,
  use a managed PostgreSQL add-on and update `DATABASE_URL`.
- Run `alembic` migrations (not yet included — recommended before real deployment;
  `Base.metadata.create_all()` in `main.py` is fine for early development only).

## Folder structure

```
gramswasthya-ai/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, middleware, routes registration
│   │   ├── config.py        # env-driven settings
│   │   ├── database.py      # SQLAlchemy engine/session
│   │   ├── models.py        # User, Conversation, Message, Report, etc.
│   │   ├── schemas.py       # Pydantic request/response models
│   │   ├── auth.py          # JWT + password hashing + guards
│   │   ├── routers/
│   │   │   ├── auth.py      # signup/login/OTP/google/me
│   │   │   ├── chat.py      # core AI chat + conversation history
│   │   │   ├── upload.py    # reports/prescriptions/skin images
│   │   │   ├── hospitals.py # OSM-based nearby facility search
│   │   │   └── admin.py     # stats/users/feedback/errors
│   │   └── services/
│   │       ├── groq_service.py         # Groq calls, system prompt, summaries
│   │       └── emergency_detector.py   # rule-based emergency keyword matcher
│   └── requirements.txt
└── frontend/
    ├── app/
    │   ├── page.tsx          # landing page
    │   ├── chat/page.tsx     # main chat UI (voice, markdown, emergency banner)
    │   ├── login/page.tsx
    │   ├── signup/page.tsx
    │   └── dashboard/page.tsx
    ├── components/
    │   ├── Navbar.tsx
    │   ├── MessageBubble.tsx
    │   └── VoiceInput.tsx
    └── lib/api.ts             # typed API client
```

## Security notes already in place
- Passwords hashed with bcrypt
- JWT auth on all protected routes
- CORS locked to `FRONTEND_ORIGIN`
- Basic security headers middleware
- Rate limiting (slowapi) on the feedback endpoint — extend to chat/auth for production
- File type + size validation on uploads
- SQL injection protection via SQLAlchemy ORM (no raw string queries)

Before going live, add: HTTPS termination at your host, stricter rate limits on
`/api/auth/*` and `/api/chat`, CSRF protection if you add cookie-based auth, and a
dependency vulnerability scan (`pip-audit`, `npm audit`).
