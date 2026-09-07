from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse


router = APIRouter(tags=["Reviews"])


@router.post(
    "/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    product = db.query(Product).filter(
        Product.id == review_data.product_id,
        Product.is_active == True,
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    completed_order = db.query(Order.id).join(
        OrderItem,
        OrderItem.order_id == Order.id,
    ).filter(
        Order.user_id == current_user.id,
        OrderItem.product_id == review_data.product_id,
        func.lower(Order.order_status) == "delivered",
    ).first()

    if not completed_order:
        raise HTTPException(
            status_code=403,
            detail="You can only review products from completed orders",
        )

    existing_review = db.query(Review.id).filter(
        Review.user_id == current_user.id,
        Review.product_id == review_data.product_id,
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=409,
            detail="You have already reviewed this product",
        )

    review = Review(
        user_id=current_user.id,
        product_id=review_data.product_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get(
    "/products/{product_id}/reviews",
    response_model=list[ReviewResponse],
)
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True,
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return db.query(Review).filter(
        Review.product_id == product_id,
        Review.status == "approved",
    ).order_by(
        Review.created_at.desc(),
    ).all()