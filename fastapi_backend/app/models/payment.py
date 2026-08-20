from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False, default="stripe")
    transaction_id = Column(String(255), nullable=False, unique=True)
    status = Column(String(30), nullable=False, default="pending")
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)

    order = relationship("Order", back_populates="payments")