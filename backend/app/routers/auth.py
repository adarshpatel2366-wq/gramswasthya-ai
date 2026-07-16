import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In-memory OTP store for demo purposes. Replace with Redis + real SMS provider
# (e.g. MSG91, Twilio) in production.
_otp_store: dict[str, str] = {}


@router.post("/signup", response_model=schemas.TokenResponse)
def signup(payload: schemas.SignupRequest, db: Session = Depends(get_db)):
    if not payload.email and not payload.phone:
        raise HTTPException(400, "Email or phone is required")

    existing = None
    if payload.email:
        existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if not existing and payload.phone:
        existing = db.query(models.User).filter(models.User.phone == payload.phone).first()
    if existing:
        raise HTTPException(400, "Account already exists")

    user = models.User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        auth_provider="email",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id})
    return schemas.TokenResponse(access_token=token)


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    query = db.query(models.User)
    user = None
    if payload.email:
        user = query.filter(models.User.email == payload.email).first()
    elif payload.phone:
        user = query.filter(models.User.phone == payload.phone).first()

    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": user.id})
    return schemas.TokenResponse(access_token=token)


@router.post("/otp/request")
def request_otp(payload: schemas.OTPRequest):
    otp = f"{random.randint(1000, 9999)}"
    _otp_store[payload.phone] = otp
    # TODO: integrate real SMS gateway (MSG91 / Twilio). For now, log it.
    print(f"[DEV] OTP for {payload.phone}: {otp}")
    return {"message": "OTP sent"}


@router.post("/otp/verify", response_model=schemas.TokenResponse)
def verify_otp(payload: schemas.OTPVerify, db: Session = Depends(get_db)):
    real_otp = _otp_store.get(payload.phone)
    if not real_otp or real_otp != payload.otp:
        raise HTTPException(400, "Invalid or expired OTP")

    user = db.query(models.User).filter(models.User.phone == payload.phone).first()
    if not user:
        user = models.User(name="User", phone=payload.phone, auth_provider="otp")
        db.add(user)
        db.commit()
        db.refresh(user)

    del _otp_store[payload.phone]
    token = create_access_token({"sub": user.id})
    return schemas.TokenResponse(access_token=token)


@router.post("/google", response_model=schemas.TokenResponse)
def google_login(payload: schemas.GoogleLoginRequest, db: Session = Depends(get_db)):
    # TODO: verify payload.id_token with google-auth library against Google's
    # public certs, then extract email/name from the verified payload.
    raise HTTPException(501, "Wire up google-auth token verification here before going live")


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user
