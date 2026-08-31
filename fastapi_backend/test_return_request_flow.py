from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import User, Order, ReturnRequest
from app.routes.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_order():
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "return-user@example.com").first()
        if not user:
            user = User(
                email="return-user@example.com",
                password=get_password_hash("password123"),
                role="customer",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        order = db.query(Order).filter(Order.id == 99).first()
        if not order:
            order = Order(
                id=99,
                user_id=user.id,
                total=120.0,
                payment_status="paid",
                order_status="delivered",
                created_at=datetime.now(timezone.utc) - timedelta(days=2),
            )
            db.add(order)
            db.commit()
            db.refresh(order)
        return user, order
    finally:
        db.close()


user, order = setup_order()

Base.metadata.create_all(bind=engine)

token_response = client.post(
    "/auth/login",
    json={"username": "return-user@example.com", "password": "password123"},
)
assert token_response.status_code == 200, token_response.text
access_token = token_response.json()["access_token"]

return_response = client.post(
    f"/orders/{order.id}/return",
    json={"reason": "damaged", "comment": "Item arrived damaged."},
    headers={"Authorization": f"Bearer {access_token}"},
)

print(return_response.status_code)
print(return_response.text)
assert return_response.status_code == 200, return_response.text
assert return_response.json()["status"] == "pending"
assert return_response.json()["reason"] == "damaged"

status_response = client.get(f"/orders/{order.id}", headers={"Authorization": f"Bearer {access_token}"})
assert status_response.status_code == 200, status_response.text
assert status_response.json()["order_status"] == "Return Requested"
