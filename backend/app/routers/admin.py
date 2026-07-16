from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models
from app.auth import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
def stats(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    total_users = db.query(func.count(models.User.id)).scalar()
    total_conversations = db.query(func.count(models.Conversation.id)).scalar()
    total_messages = db.query(func.count(models.Message.id)).scalar()
    emergency_messages = (
        db.query(func.count(models.Message.id)).filter(models.Message.is_emergency.is_(True)).scalar()
    )
    total_reports = db.query(func.count(models.Report.id)).scalar()
    return {
        "total_users": total_users,
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "emergency_messages": emergency_messages,
        "total_reports_uploaded": total_reports,
    }


@router.get("/users")
def list_users(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    return db.query(models.User).all()


@router.get("/feedback")
def list_feedback(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    return db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).all()


@router.get("/errors")
def list_errors(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    return (
        db.query(models.ErrorLog)
        .order_by(models.ErrorLog.created_at.desc())
        .limit(200)
        .all()
    )


@router.get("/reports")
def list_all_reports(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    return db.query(models.Report).order_by(models.Report.created_at.desc()).all()
