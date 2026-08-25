import asyncio
import os
import smtplib
from email.message import EmailMessage
from typing import Any

from fastapi import BackgroundTasks, WebSocket
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User


class NotificationConnectionManager:
    def __init__(self):
        self.connections: dict[int, set[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.connections.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        sockets = self.connections.get(user_id, set())
        sockets.discard(websocket)
        if not sockets:
            self.connections.pop(user_id, None)

    async def publish(self, user_id: int, payload: dict[str, Any]):
        sockets = tuple(self.connections.get(user_id, set()))
        for websocket in sockets:
            try:
                await websocket.send_json(payload)
            except Exception:
                self.disconnect(user_id, websocket)


manager = NotificationConnectionManager()


def send_notification_email(recipient: str, subject: str, message: str):
    host = os.getenv("SMTP_HOST", "").strip()
    sender = os.getenv("SMTP_FROM", "").strip()
    if not host or not sender:
        return

    email = EmailMessage()
    email["From"] = sender
    email["To"] = recipient
    email["Subject"] = subject
    email.set_content(message)
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    with smtplib.SMTP(host, port, timeout=10) as smtp:
        if use_tls:
            smtp.starttls()
        if username:
            smtp.login(username, password)
        smtp.send_message(email)


def create_notification(
    db: Session,
    user: User,
    notification_type: str,
    message: str,
    order_id: int | None = None,
    event_key: str | None = None,
    event_name: str | None = None,
    background_tasks: BackgroundTasks | None = None,
):
    if event_key and db.query(Notification).filter(Notification.event_key == event_key).first():
        return None

    notification = Notification(
        user_id=user.id,
        order_id=order_id,
        type=notification_type,
        message=message,
        event_key=event_key,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    payload = {
        "event": event_name or notification_type,
        "notification": {
            "id": notification.id,
            "type": notification.type,
            "message": notification.message,
            "read_status": notification.read_status,
            "timestamp": notification.timestamp.isoformat(),
            "order_id": notification.order_id,
        },
    }
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.publish(user.id, payload))
    except RuntimeError:
        pass

    if background_tasks:
        background_tasks.add_task(
            send_notification_email,
            user.email,
            notification_type.replace("_", " ").title(),
            message,
        )
    return notification
