from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Alert
from app.schemas import AlertItem

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertItem])
def list_alerts(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return (
        db.query(Alert)
        .order_by(Alert.triggered_at.desc(), Alert.id.desc())
        .limit(limit)
        .all()
    )
