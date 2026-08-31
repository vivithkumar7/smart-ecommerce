import os
from datetime import datetime, timedelta, timezone

import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.cart import Cart
from app.models.order import Order, OrderItem
from app.models.order import ORDER_STATUSES
from app.models.payment import Payment
from app.models.return_request import ReturnRequest
from app.schemas.order import (
    CheckoutRequest,
    CheckoutResponse,
    OrderResponse,
    ReturnRequestCreate,
    ReturnRequestResponse,
)
from app.schemas.order_status import OrderStatusUpdateRequest
from app.services.notifications import create_notification


router = APIRouter(tags=["Checkout"])


def get_tax_rate():
    try:
        rate = float(os.getenv("TAX_RATE", "0.02"))
    except (TypeError, ValueError):
        rate = 0.02

    if rate > 0.1:
        rate = 0.02

    return rate


TAX_RATE = get_tax_rate()
CURRENCY = os.getenv("STRIPE_CURRENCY", "usd").lower()
CHECKOUT_MODE = os.getenv("CHECKOUT_MODE", "stripe").lower()
ORDER_STATUS_ADMIN_KEY = os.getenv("ORDER_STATUS_ADMIN_KEY", "").strip()
RETURN_WINDOW_DAYS = int(os.getenv("RETURN_WINDOW_DAYS", "7"))


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return orders


@router.post("/orders/{order_id}/return", response_model=ReturnRequestResponse)
def request_return(
    order_id: int,
    request: ReturnRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.order_status.lower() != "delivered":
        raise HTTPException(status_code=400, detail="Returns are only allowed for delivered orders")

    if not request.reason or not request.reason.strip():
        raise HTTPException(status_code=400, detail="Return reason is required")

    if order.created_at is None:
        raise HTTPException(status_code=400, detail="Order is missing a valid delivery date")

    order_time = order.created_at
    if order_time.tzinfo is None:
        order_time = order_time.replace(tzinfo=timezone.utc)
    else:
        order_time = order_time.astimezone(timezone.utc)

    return_deadline = order_time + timedelta(days=RETURN_WINDOW_DAYS)
    if datetime.now(timezone.utc) > return_deadline:
        raise HTTPException(status_code=400, detail=f"Return window expired. Returns must be requested within {RETURN_WINDOW_DAYS} days of delivery.")

    existing_request = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.order_id == order_id, ReturnRequest.user_id == current_user.id)
        .first()
    )
    if existing_request:
        raise HTTPException(status_code=400, detail="A return request already exists for this order")

    return_request = ReturnRequest(
        order_id=order.id,
        user_id=current_user.id,
        reason=request.reason.strip(),
        comment=request.comment.strip() if request.comment and request.comment.strip() else None,
        status="pending",
    )
    db.add(return_request)
    order.order_status = "Return Requested"
    db.commit()
    db.refresh(return_request)
    create_notification(
        db,
        current_user,
        "return_requested",
        f"Return requested for order #{order.id}. We will review it shortly.",
        order_id=order.id,
        event_key=f"order:{order.id}:return_requested",
        background_tasks=None,
    )
    return return_request


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    checkout_request: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
):
    selected_payment = (checkout_request.payment_method or "card").strip().lower()
    is_cash_on_delivery = selected_payment in {"cod", "cashondelivery", "cash_on_delivery", "cash on delivery"}

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    subtotal = sum(item.unit_price * item.quantity for item in cart.items)
    total = round(subtotal * (1 + TAX_RATE), 2)
    amount_in_cents = int(round(total * 100))

    order = Order(
        user_id=current_user.id,
        total=total,
        payment_status="pending",
        order_status="pending",
    )
    db.add(order)
    db.flush()

    line_items = []
    for item in cart.items:
        db.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.unit_price,
            subtotal=round(item.unit_price * item.quantity, 2),
        ))
        line_items.append({
            "price_data": {
                "currency": CURRENCY,
                "product_data": {"name": item.product.name},
                "unit_amount": int(round(item.unit_price * 100)),
            },
            "quantity": item.quantity,
        })

    if is_cash_on_delivery:
        payment = Payment(
            order_id=order.id,
            amount=total,
            payment_method="cash_on_delivery",
            transaction_id=f"cod_{order.id}",
            status="pending",
        )
        db.add(payment)
        order.payment_status = "pending"
        order.order_status = "pending"
        for item in list(cart.items):
            db.delete(item)
        db.commit()
        create_notification(
            db,
            current_user,
            "order_confirmed",
            f"Order #{order.id} is confirmed. Cash on Delivery selected. Waiting for payment on delivery.",
            order_id=order.id,
            event_key=f"order:{order.id}:cod:pending",
            background_tasks=background_tasks,
        )
        return CheckoutResponse(
            order_id=order.id,
            amount=total,
            currency=CURRENCY,
            payment_intent_id=f"cod_{order.id}",
            checkout_session_id=f"cod_session_{order.id}",
            checkout_url=None,
            payment_status=order.payment_status,
            order_status=order.order_status,
        )

    stripe_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    if CHECKOUT_MODE == "mock":
        payment_intent_id = f"mock_pi_{order.id}"
        checkout_session_id = f"mock_cs_{order.id}"
        payment = Payment(
            order_id=order.id,
            amount=total,
            payment_method="mock",
            transaction_id=payment_intent_id,
            status="succeeded",
        )
        db.add(payment)
        order.payment_status = "paid"
        order.order_status = "paid"
        for item in list(cart.items):
            db.delete(item)
        db.commit()
        create_notification(
            db,
            current_user,
            "order_confirmed",
            f"Order #{order.id} was confirmed. Payment was successful.",
            order_id=order.id,
            event_key=f"order:{order.id}:confirmed",
            background_tasks=background_tasks,
        )
        return CheckoutResponse(
            order_id=order.id,
            amount=total,
            currency=CURRENCY,
            payment_intent_id=payment_intent_id,
            checkout_session_id=checkout_session_id,
            checkout_url=None,
            payment_status=order.payment_status,
            order_status=order.order_status,
        )

    if (
        not stripe_key
        or stripe_key in {"sk_test_your_real_stripe_key", "sk_test_..."}
        or "<your" in stripe_key.lower()
        or "your_" in stripe_key.lower()
    ):
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Stripe is not configured. Replace STRIPE_SECRET_KEY with a real Stripe test key.",
        )

    stripe.api_key = stripe_key
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency=CURRENCY,
            metadata={"order_id": str(order.id)},
        )
        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            client_reference_id=str(order.id),
            metadata={
                "order_id": str(order.id),
                "amount": str(amount_in_cents),
                "currency": CURRENCY,
            },
            payment_intent_data={"metadata": {"order_id": str(order.id)}},
            success_url=os.getenv("STRIPE_SUCCESS_URL", "http://localhost:5173/checkout?success=true"),
            cancel_url=os.getenv("STRIPE_CANCEL_URL", "http://localhost:5173/checkout?cancelled=true"),
        )
    except stripe.error.AuthenticationError as error:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Stripe secret key is invalid. Set STRIPE_SECRET_KEY to a real sk_test_ key.",
        ) from error
    except stripe.error.StripeError as error:
        db.rollback()
        message = error.user_message or str(error)
        raise HTTPException(status_code=502, detail=f"Stripe error: {message}") from error

    payment = Payment(
        order_id=order.id,
        amount=total,
        payment_method="stripe",
        transaction_id=payment_intent.id,
        status=payment_intent.status,
    )
    db.add(payment)
    for item in list(cart.items):
        db.delete(item)
    db.commit()

    return CheckoutResponse(
        order_id=order.id,
        amount=total,
        currency=CURRENCY,
        payment_intent_id=payment_intent.id,
        checkout_session_id=checkout_session.id,
        checkout_url=checkout_session.url,
        payment_status=order.payment_status,
        order_status=order.order_status,
    )   


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    request: OrderStatusUpdateRequest,
    x_admin_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    if not ORDER_STATUS_ADMIN_KEY or x_admin_key != ORDER_STATUS_ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Valid order status admin key is required")
    if request.order_status not in ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid order status")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.order_status == request.order_status:
        return {"order_id": order.id, "order_status": order.order_status}

    order.order_status = request.order_status
    db.commit()
    create_notification(
        db,
        order.user,
        "order_status_updated",
        f"Order #{order.id} is now {request.order_status}.",
        order_id=order.id,
        event_key=f"order:{order.id}:status:{request.order_status}",
        background_tasks=background_tasks,
    )
    return {"order_id": order.id, "order_status": order.order_status}


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
    if CHECKOUT_MODE == "mock":
        return {"received": True, "mode": "mock"}

    if not webhook_secret or "your_" in webhook_secret.lower():
        raise HTTPException(status_code=503, detail="Stripe webhook is not configured")

    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as error:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook") from error

    if event["type"] not in {
        "checkout.session.completed",
        "payment_intent.succeeded",
        "payment_intent.payment_failed",
    }:
        return {"received": True}

    intent = event["data"]["object"]
    order_id = intent.get("metadata", {}).get("order_id")
    payment_intent_id = intent.get("payment_intent")
    if event["type"].startswith("payment_intent"):
        payment_intent_id = intent.get("id")
    if not order_id:
        return {"received": True}

    order = db.query(Order).filter(Order.id == int(order_id)).first()
    payment = db.query(Payment).filter(Payment.order_id == int(order_id)).first()
    if order and payment:
        succeeded = event["type"] in {
            "checkout.session.completed",
            "payment_intent.succeeded",
        }
        payment.status = "succeeded" if succeeded else intent.get("status", "failed")
        if payment_intent_id:
            payment.transaction_id = payment_intent_id
        order.payment_status = "paid" if succeeded else "failed"
        if succeeded:
            order.order_status = "paid"
        db.commit()
        create_notification(
            db,
            order.user,
            "payment_success" if succeeded else "payment_failure",
            (
                f"Payment for order #{order.id} was successful."
                if succeeded
                else f"Payment for order #{order.id} failed. Please try again."
            ),
            order_id=order.id,
            event_key=f"order:{order.id}:payment:{'success' if succeeded else 'failure'}",
            event_name="order_status_updated" if succeeded else None,
            background_tasks=background_tasks,
        )

    return {"received": True}