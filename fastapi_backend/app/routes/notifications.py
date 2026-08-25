from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.notification import Notification
from app.schemas.notification import (
    MarkNotificationsReadRequest,
    NotificationResponse,
)
from app.services.notifications import manager


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Notification).filter(
        Notification.user_id == current_user.id,
    ).order_by(Notification.timestamp.desc()).all()


@router.post("/read", response_model=dict[str, int])
def mark_notifications_read(
    request: MarkNotificationsReadRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if request.notification_ids is not None:
        query = query.filter(Notification.id.in_(request.notification_ids))
    updated = query.update({Notification.read_status: True}, synchronize_session=False)
    db.commit()
    return {"updated": updated}


@router.websocket("/ws")
async def notification_websocket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
