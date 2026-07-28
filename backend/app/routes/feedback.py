"""
Feedback routes for application feedback and recommendation acceptance tracking.
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.feedback import Feedback
from app.services.audit import log_audit_event

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackCreateRequest(BaseModel):
    category: str = Field(..., min_length=2, max_length=100)
    rating: int = Field(..., ge=1, le=5)
    message: str = Field(..., min_length=3, max_length=2000)
    source_page: Optional[str] = Field(default=None, max_length=100)
    accepted_recommendation: Optional[bool] = None


def _serialize_feedback(entry: Feedback) -> Dict[str, Any]:
    return {
        "id": entry.id,
        "category": entry.category,
        "rating": entry.rating,
        "message": entry.message,
        "source_page": entry.source_page,
        "accepted_recommendation": entry.accepted_recommendation,
        "submitted_by": entry.submitted_by,
        "user_role": entry.user_role,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }


def _build_summary(db: Session) -> Dict[str, Any]:
    entries = db.query(Feedback).all()
    total = len(entries)
    average_rating = round(sum(item.rating for item in entries) / total, 1) if total else 0.0

    acceptance_entries = [item for item in entries if item.accepted_recommendation is not None]
    accepted_count = sum(1 for item in acceptance_entries if item.accepted_recommendation)
    rejected_count = sum(1 for item in acceptance_entries if item.accepted_recommendation is False)
    acceptance_rate = (
        round((accepted_count / len(acceptance_entries)) * 100, 1)
        if acceptance_entries
        else None
    )

    return {
        "total_feedback": total,
        "average_rating": average_rating,
        "recommendation_acceptance_rate": acceptance_rate,
        "accepted_recommendations": accepted_count,
        "rejected_recommendations": rejected_count,
    }


@router.get("", summary="List feedback entries")
def list_feedback(limit: int = 20, db: Session = Depends(get_db)) -> Dict[str, Any]:
    entries = (
        db.query(Feedback)
        .order_by(Feedback.created_at.desc(), Feedback.id.desc())
        .limit(max(1, min(limit, 100)))
        .all()
    )
    return {
        **_build_summary(db),
        "entries": [_serialize_feedback(entry) for entry in entries],
    }


@router.post("", status_code=201, summary="Submit feedback")
def submit_feedback(
    payload: FeedbackCreateRequest,
    db: Session = Depends(get_db),
    x_user_name: str | None = Header(default=None, alias="X-User-Name"),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
) -> Dict[str, Any]:
    entry = Feedback(
        category=payload.category.strip(),
        rating=payload.rating,
        message=payload.message.strip(),
        source_page=payload.source_page.strip() if payload.source_page else None,
        accepted_recommendation=payload.accepted_recommendation,
        submitted_by=x_user_name.strip() if x_user_name else None,
        user_role=x_user_role.strip() if x_user_role else None,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    log_audit_event(
        action="submit_feedback",
        entity_type="feedback",
        entity_id=str(entry.id),
        details={
            "category": entry.category,
            "rating": entry.rating,
            "accepted_recommendation": entry.accepted_recommendation,
            "source_page": entry.source_page,
        },
        actor=entry.submitted_by,
        actor_role=entry.user_role,
        source="feedback.submit",
        db=db,
    )
    return {"status": "success", "entry": _serialize_feedback(entry), "summary": _build_summary(db)}


@router.delete("/clear", summary="Clear feedback")
def clear_feedback(db: Session = Depends(get_db)) -> Dict[str, Any]:
    deleted = db.query(Feedback).delete()
    db.commit()
    log_audit_event(
        action="clear_feedback",
        entity_type="feedback",
        details={"deleted": deleted},
        source="feedback.clear",
        db=db,
    )
    return {"status": "success", "deleted": deleted}