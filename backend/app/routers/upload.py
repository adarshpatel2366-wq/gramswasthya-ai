import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.auth import get_current_user
from app.services.groq_service import summarize_report
from app.config import settings

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

ALLOWED_TYPES = {"report", "prescription", "skin_image"}
LOCAL_UPLOAD_DIR = "uploaded_files"
os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE_MB = 10


def _save_locally(file: UploadFile) -> str:
    """Fallback local storage. Swap for Cloudinary in production (see cloudinary_service)."""
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(LOCAL_UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        content = file.file.read()
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(413, f"File too large (max {MAX_FILE_SIZE_MB}MB)")
        f.write(content)
    return f"/{LOCAL_UPLOAD_DIR}/{filename}"


@router.post("")
def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if file_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"file_type must be one of {ALLOWED_TYPES}")

    allowed_ext = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_ext:
        raise HTTPException(400, "Unsupported file format")

    if settings.cloudinary_cloud_name:
        # TODO: use cloudinary.uploader.upload(file.file) when credentials are set
        file_url = _save_locally(file)
    else:
        file_url = _save_locally(file)

    ai_summary = None
    if file_type in ("report", "prescription"):
        # NOTE: for real OCR, run the PDF/image through an OCR step (e.g.
        # pytesseract or a cloud OCR API) to get extracted_text before summarizing.
        extracted_text_placeholder = (
            f"[Extracted text from uploaded {file_type} would go here after OCR]"
        )
        try:
            ai_summary = summarize_report(extracted_text_placeholder, file_type)
        except Exception:
            ai_summary = "Summary unavailable right now — please try again shortly."
    elif file_type == "skin_image":
        ai_summary = (
            "Skin image received. For an AI description of visible characteristics "
            "(not a diagnosis), ask about it in the chat and attach context such as "
            "how long you've had it, itching/pain, and any changes."
        )

    report = models.Report(
        user_id=user.id, file_url=file_url, file_type=file_type, ai_summary=ai_summary
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "id": report.id,
        "file_url": report.file_url,
        "file_type": report.file_type,
        "ai_summary": report.ai_summary,
    }


@router.get("")
def list_uploads(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    reports = db.query(models.Report).filter(models.Report.user_id == user.id).all()
    return reports
