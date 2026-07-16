from pydantic import BaseModel, EmailStr
from typing import Optional, List


# ---------- Auth ----------
class SignupRequest(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str


class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str


class OTPRequest(BaseModel):
    phone: str


class OTPVerify(BaseModel):
    phone: str
    otp: str


class GoogleLoginRequest(BaseModel):
    id_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: str
    is_admin: bool

    class Config:
        from_attributes = True


# ---------- Chat ----------
class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    language: Optional[str] = "auto"  # hi | en | hinglish | auto
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    is_emergency: bool
    emergency_advice: Optional[str] = None
    detected_language: str


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    is_emergency: bool
    created_at: str

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: str
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True


# ---------- Hospitals ----------
class HospitalOut(BaseModel):
    name: str
    type: str
    address: Optional[str] = None
    distance_km: Optional[float] = None
    latitude: float
    longitude: float
    open_now: Optional[bool] = None
