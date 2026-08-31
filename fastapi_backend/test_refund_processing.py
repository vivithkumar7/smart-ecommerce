from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import User, Order
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


def test_refund_processing_flow():
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "refund-user@example.com").first()
        if not user:
            user = User(
                email="refund-user@example.com",
                password=get_password_hash("password123"),
                role="customer",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        order = db.query(Order).filter(Order.id == 150).first()
        if order:
            db.delete(order)
            db.commit()

        order = Order(
            id=150,
            user_id=user.id,
            total=250.0,
            payment_status="paid",
            order_status="delivered",
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        db.add(order)
        db.commit()
        db.refresh(order)
    finally:
        db.close()

    login_response = client.post(
        "/auth/login",
        json={"username": "refund-user@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200, login_response.text
    access_token = login_response.json()["access_token"]

    return_response = client.post(
        f"/orders/{order.id}/return",
        json={"reason": "wrong item"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert return_response.status_code == 200, return_response.text

    admin_headers = {"X-Admin-Key": "smart-admin-local-key"}
    approve_response = client.patch(
        f"/return-requests/{return_response.json()['id']}",
        json={"status": "approved"},
        headers=admin_headers,
    )
    assert approve_response.status_code == 200, approve_response.text
    assert approve_response.json()["status"] == "approved"

    refund_response = client.get(f"/orders/{order.id}/refunds", headers=admin_headers)
    assert refund_response.status_code == 200, refund_response.text
    refunds = refund_response.json()
    assert len(refunds) == 1, refunds
    assert refunds[0]["amount"] == 250.0
    assert refunds[0]["status"] in {"pending", "processed"}
