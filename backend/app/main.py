from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app import models, schemas
from app.routers import auth, chat, upload, hospitals, admin

# Create tables (use Alembic migrations instead of this in real production)
Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="GramSwasthya AI API",
    description="AI Healthcare Assistant backend for rural India",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic security headers (extend with a dedicated middleware/library for full CSP in prod)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(hospitals.router)
app.include_router(admin.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}


@app.post("/api/feedback")
@limiter.limit("10/minute")
def submit_feedback(request: Request, message: str, rating: str = None, db: Session = Depends(get_db)):
    fb = models.Feedback(message=message, rating=rating)
    db.add(fb)
    db.commit()
    return {"message": "Thank you for your feedback"}
