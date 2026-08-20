from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    Boolean,
    DateTime
)

from sqlalchemy.sql import func

from app.core.database import Base


class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    category = Column(
        String(100),
        nullable=False,
        index=True
    )

    price = Column(
        Float,
        nullable=False
    )

    popularity = Column(
        Float,
        default=0,
        nullable=False
    )

    stock = Column(
        Integer,
        default=0,
        nullable=False
    )

    image_url = Column(
        String(500),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )