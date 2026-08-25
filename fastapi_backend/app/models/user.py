from sqlalchemy import Boolean, Column, Integer, String
from app.core.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False,
        default="customer",
        server_default="customer",
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )