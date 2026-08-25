from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    type = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    read_status = Column(Boolean, nullable=False, default=False, index=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    event_key = Column(String(255), unique=True, nullable=True)

    user = relationship("User")
    order = relationship("Order")
