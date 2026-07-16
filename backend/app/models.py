import uuid
import datetime as dt
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)  # null if OAuth/OTP-only
    auth_provider = Column(String, default="email")  # email | google | otp
    is_admin = Column(Boolean, default=False)
    village_or_city = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    preferred_language = Column(String, default="auto")  # hi | en | hinglish | auto
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user")
    reports = relationship("Report", back_populates="user")
    health_profile = relationship("HealthProfile", back_populates="user", uselist=False)


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    age = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    known_conditions = Column(Text, nullable=True)   # comma separated
    allergies = Column(Text, nullable=True)
    medications = Column(Text, nullable=True)

    user = relationship("User", back_populates="health_profile")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, default="New conversation")
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=gen_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(Enum("user", "assistant", "system", name="role_enum"), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String, nullable=True)
    is_emergency = Column(Boolean, default=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # report | prescription | skin_image
    ai_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    user = relationship("User", back_populates="reports")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    message = Column(Text, nullable=False)
    rating = Column(String, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    source = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
