from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

RETURN_REQUEST_STATUSES = ("pending", "approved", "rejected")


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reason = Column(String(255), nullable=False)
    comment = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending", server_default="pending")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    order = relationship("Order", back_populates="return_requests")
    user = relationship("User")
