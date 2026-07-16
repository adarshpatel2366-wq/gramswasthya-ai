from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from app.services.emergency_detector import detect_emergency
from app.services.groq_service import get_ai_reply, generate_conversation_summary

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=schemas.ChatResponse)
def chat(
    payload: schemas.ChatRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Get or create conversation
    if payload.conversation_id:
        convo = (
            db.query(models.Conversation)
            .filter(
                models.Conversation.id == payload.conversation_id,
                models.Conversation.user_id == user.id,
            )
            .first()
        )
        if not convo:
            raise HTTPException(404, "Conversation not found")
    else:
        convo = models.Conversation(user_id=user.id, title=payload.message[:60])
        db.add(convo)
        db.commit()
        db.refresh(convo)

    # Fast, deterministic emergency check runs first so we never delay this guidance
    is_emergency, category, advice = detect_emergency(payload.message)

    # Save user message
    user_msg = models.Message(
        conversation_id=convo.id,
        role="user",
        content=payload.message,
        language=payload.language,
        is_emergency=is_emergency,
    )
    db.add(user_msg)
    db.commit()

    # Pull recent history (last 20 messages) for context
    history = (
        db.query(models.Message)
        .filter(models.Message.conversation_id == convo.id)
        .order_by(models.Message.created_at.asc())
        .limit(20)
        .all()
    )

    try:
        ai_text = get_ai_reply(history[:-1], payload.message, payload.language or "auto")
    except Exception as e:
        db.add(models.ErrorLog(source="groq_service.get_ai_reply", message=str(e)))
        db.commit()
        raise HTTPException(502, "AI service is temporarily unavailable. Please try again.")

    if is_emergency:
        ai_text = f"⚠️ **This looks like it may be an emergency.**\n\n{advice}\n\n{ai_text}"

    assistant_msg = models.Message(
        conversation_id=convo.id,
        role="assistant",
        content=ai_text,
        is_emergency=is_emergency,
    )
    db.add(assistant_msg)
    db.commit()

    return schemas.ChatResponse(
        conversation_id=convo.id,
        reply=ai_text,
        is_emergency=is_emergency,
        emergency_advice=advice,
        detected_language=payload.language or "auto",
    )


@router.get("/conversations", response_model=list[schemas.ConversationOut])
def list_conversations(
    db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    convos = (
        db.query(models.Conversation)
        .filter(models.Conversation.user_id == user.id)
        .order_by(models.Conversation.created_at.desc())
        .all()
    )
    return convos


@router.get("/conversations/{conversation_id}", response_model=schemas.ConversationOut)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    convo = (
        db.query(models.Conversation)
        .filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user.id)
        .first()
    )
    if not convo:
        raise HTTPException(404, "Conversation not found")
    return convo


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    convo = (
        db.query(models.Conversation)
        .filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user.id)
        .first()
    )
    if not convo:
        raise HTTPException(404, "Conversation not found")
    db.delete(convo)
    db.commit()
    return {"message": "Deleted"}


@router.get("/conversations/{conversation_id}/summary")
def summarize(
    conversation_id: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    convo = (
        db.query(models.Conversation)
        .filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user.id)
        .first()
    )
    if not convo:
        raise HTTPException(404, "Conversation not found")
    summary = generate_conversation_summary(convo.messages)
    return {"summary": summary}
