from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.product_view import ProductView
from app.models.review import Review
from app.routes.product import add_rating_aggregates
from app.schemas.product import ProductResponse


router = APIRouter(tags=["Recommendations"])


def _rating_map(db: Session, product_ids: list[int]):
    if not product_ids:
        return {}
    rows = db.query(
        Review.product_id,
        func.avg(Review.rating),
    ).filter(
        Review.product_id.in_(product_ids),
        Review.status == "approved",
    ).group_by(Review.product_id).all()
    return {product_id: float(rating) for product_id, rating in rows}


def _active_products(db: Session):
    products = db.query(Product).filter(Product.is_active == True).all()
    return products, {product.id: product for product in products}


def _similarity_score(candidate: Product, source: Product):
    score = 0
    if candidate.category == source.category:
        score += 4
    price_gap = abs(candidate.price - source.price) / max(source.price, 1)
    return score + max(0, 2 - (price_gap * 2))


@router.get("/recommendations/{user_id}", response_model=list[ProductResponse])
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    products, products_by_id = _active_products(db)
    if not products:
        return []

    recent_cutoff = datetime.utcnow() - timedelta(days=30)
    viewed_rows = db.query(
        ProductView.product_id,
        ProductView.viewed_at,
    ).filter(
        ProductView.user_id == user_id,
    ).order_by(ProductView.viewed_at.desc()).all()
    viewed_ids = {product_id for product_id, _ in viewed_rows}
    user_view_counts = {}
    for product_id, viewed_at in viewed_rows:
        if viewed_at and viewed_at >= recent_cutoff:
            user_view_counts[product_id] = user_view_counts.get(product_id, 0) + 1

    viewed_products = [
        (
            products_by_id[product_id],
            1 + min(user_view_counts.get(product_id, 0), 3) * 0.25,
        )
        for product_id, _ in viewed_rows
        if product_id in products_by_id
    ]

    global_view_counts = dict(db.query(
        ProductView.product_id,
        func.count(ProductView.id),
    ).filter(
        ProductView.viewed_at >= recent_cutoff,
    ).group_by(ProductView.product_id).all())

    purchased_rows = db.query(
        OrderItem.product_id,
        OrderItem.quantity,
        Product.category,
    ).join(
        Product, Product.id == OrderItem.product_id,
    ).join(Order, Order.id == OrderItem.order_id).filter(
        Order.user_id == user_id,
        Order.order_status.notin_(["cancelled", "returned", "refunded", "rejected"]),
    ).all()
    purchased_ids = {product_id for product_id, _, _ in purchased_rows}
    purchased_products = [
        (products_by_id[product_id], min(quantity, 3) * 0.5)
        for product_id, quantity, _ in purchased_rows
        if product_id in products_by_id
    ]
    preferred_categories = {category for _, _, category in purchased_rows if category}
    preferred_categories.update(
        products_by_id[product_id].category
        for product_id in viewed_ids
        if product_id in products_by_id
    )
    ratings = _rating_map(db, list(products_by_id))
    max_popularity = max((product.popularity or 0 for product in products), default=1) or 1

    scored = []
    for product in products:
        if product.id in viewed_ids or product.id in purchased_ids:
            continue
        score = 0
        if product.category in preferred_categories:
            score += 5
        score += max(
            (_similarity_score(product, viewed_product) * view_weight
             for viewed_product, view_weight in viewed_products),
            default=0,
        )
        score += max(
            (_similarity_score(product, purchased_product) * purchase_weight
             for purchased_product, purchase_weight in purchased_products),
            default=0,
        )
        score += global_view_counts.get(product.id, 0) * 1.5
        score += (product.popularity or 0) / max_popularity
        score += (ratings.get(product.id, 0) / 5) * 2
        scored.append((score, product))

    scored.sort(key=lambda item: (item[0], item[1].popularity or 0), reverse=True)
    recommendations = [product for _, product in scored[:8]]
    if len(recommendations) < 8:
        seen = {product.id for product in recommendations} | viewed_ids | purchased_ids
        fallback = sorted(
            (product for product in products if product.id not in seen),
            key=lambda product: (
                global_view_counts.get(product.id, 0) * 1.5
                + (ratings.get(product.id, 0) / 5) * 2
                + (product.popularity or 0) / max_popularity
            ),
            reverse=True,
        )
        recommendations.extend(fallback[:8 - len(recommendations)])
    return add_rating_aggregates(recommendations, db)


@router.get("/products/{product_id}/similar", response_model=list[ProductResponse])
def get_similar_products(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    products, _ = _active_products(db)
    ratings = _rating_map(db, [item.id for item in products])
    max_popularity = max((item.popularity or 0 for item in products), default=1) or 1
    scored = []
    for candidate in products:
        if candidate.id == product.id:
            continue
        price_gap = abs(candidate.price - product.price) / max(product.price, 1)
        score = (8 if candidate.category == product.category else 0)
        score += max(0, 3 - (price_gap * 3))
        score += (ratings.get(candidate.id, 0) / 5) * 2
        score += (candidate.popularity or 0) / max_popularity
        scored.append((score, candidate))
    scored.sort(key=lambda item: item[0], reverse=True)
    return add_rating_aggregates([product for _, product in scored[:8]], db)


@router.get("/products/trending", response_model=list[ProductResponse])
def get_trending_products(db: Session = Depends(get_db)):
    products, products_by_id = _active_products(db)
    cutoff = datetime.utcnow() - timedelta(days=30)
    view_counts = dict(db.query(
        ProductView.product_id,
        func.count(ProductView.id),
    ).filter(ProductView.viewed_at >= cutoff).group_by(ProductView.product_id).all())
    ratings = _rating_map(db, list(products_by_id))
    max_popularity = max((product.popularity or 0 for product in products), default=1) or 1
    ranked = sorted(
        products,
        key=lambda product: (
            view_counts.get(product.id, 0) * 4
            + (product.popularity or 0) / max_popularity
            + (ratings.get(product.id, 0) / 5) * 2
        ),
        reverse=True,
    )
    return add_rating_aggregates(ranked[:8], db)