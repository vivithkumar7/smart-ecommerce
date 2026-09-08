from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.order import Order
from app.models.product import Product
from app.schemas.email import EmailMessageResponse, ReturnStatusEmailRequest
from app.services.notifications import send_notification_email


router = APIRouter(prefix="/emails", tags=["Email"])


def queue_email(background_tasks: BackgroundTasks, recipient: str, subject: str, message: str):
    background_tasks.add_task(send_notification_email, recipient, subject, message)


@router.post("/orders/{order_id}/delivered", response_model=EmailMessageResponse)
def send_delivered_order_email(
    order_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if str(order.order_status).lower() != "delivered":
        raise HTTPException(status_code=400, detail="The order has not been delivered")

    queue_email(
        background_tasks,
        current_user.email,
        f"Your SmartShop order #{order.id} was delivered",
        f"Your order #{order.id} has been delivered successfully. Thank you for shopping with SmartShop.",
    )
    return {"message": "Delivered-order email queued."}


@router.post("/premium-offer", response_model=EmailMessageResponse)
def send_premium_offer_email(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    queue_email(
        background_tasks,
        current_user.email,
        "Your SmartShop premium offer",
        "Enjoy up to 40% off premium essentials. Sign in, choose a premium product, and add it to your cart. The offer is applied at checkout.",
    )
    return {"message": "Premium-offer email queued."}


@router.post("/recommendations", response_model=EmailMessageResponse)
def send_recommendation_email(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    products = db.query(Product).filter(Product.is_active == True).order_by(Product.popularity.desc()).limit(5).all()
    product_lines = "\n".join(f"- {product.name} (₹{product.price:,.2f})" for product in products)
    queue_email(
        background_tasks,
        current_user.email,
        "Product recommendations from SmartShop",
        f"Here are a few products selected for you:\n\n{product_lines}\n\nVisit SmartShop to explore more.",
    )
    return {"message": "Recommendation email queued."}


@router.post("/orders/{order_id}/return-status", response_model=EmailMessageResponse)
def send_return_status_email(
    order_id: int,
    request: ReturnStatusEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    status = request.status.strip()
    detail = request.message.strip() if request.message else f"Your return request for order #{order.id} is now {status.lower()}."
    queue_email(
        background_tasks,
        current_user.email,
        f"Return update for SmartShop order #{order.id}",
        detail,
    )
    return {"message": "Return-status email queued."}