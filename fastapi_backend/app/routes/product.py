from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.product import Product
from app.models.review import Review
from app.models.product_view import ProductView
from app.dependencies.auth import get_current_user_optional
from app.schemas.product import ProductResponse


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


def add_rating_aggregates(products, db: Session):
    if not products:
        return products

    product_ids = [product.id for product in products]
    aggregates = db.query(
        Review.product_id,
        func.avg(Review.rating).label("average_rating"),
        func.count(Review.id).label("total_reviews"),
    ).filter(
        Review.product_id.in_(product_ids),
        Review.status == "approved",
    ).group_by(
        Review.product_id,
    ).all()
    aggregate_by_product = {
        product_id: (float(average_rating), int(total_reviews))
        for product_id, average_rating, total_reviews in aggregates
    }

    for product in products:
        product.average_rating, product.total_reviews = aggregate_by_product.get(
            product.id,
            (None, 0),
        )

    return products


# =====================================================
# GET ALL PRODUCTS
# =====================================================

@router.get(
    "",
    response_model=list[ProductResponse]
)
def get_products(

    category: Optional[str] = None,

    min_price: Optional[float] = Query(
        None,
        ge=0
    ),

    max_price: Optional[float] = Query(
        None,
        ge=0
    ),

    min_popularity: Optional[float] = Query(
        None,
        ge=0
    ),

    in_stock: Optional[bool] = None,

    db: Session = Depends(get_db)
):

    query = db.query(Product).filter(
        Product.is_active == True
    )

    # Category filter
    if category:

        query = query.filter(
            Product.category == category
        )

    # Minimum price
    if min_price is not None:

        query = query.filter(
            Product.price >= min_price
        )

    # Maximum price
    if max_price is not None:

        query = query.filter(
            Product.price <= max_price
        )

    # Popularity
    if min_popularity is not None:

        query = query.filter(
            Product.popularity >= min_popularity
        )

    # Stock availability
    if in_stock is True:

        query = query.filter(
            Product.stock > 0
        )

    elif in_stock is False:

        query = query.filter(
            Product.stock == 0
        )

    # Popular products first
    query = query.order_by(
        Product.popularity.desc()
    )

    return add_rating_aggregates(query.all(), db)


# =====================================================
# GET PRODUCT BY ID
# =====================================================

@router.get(
    "/categories",
    response_model=list[str],
)
def get_product_categories(db: Session = Depends(get_db)):
    return [
        category
        for (category,) in db.query(Product.category)
        .filter(Product.is_active == True, Product.category.isnot(None))
        .distinct()
        .order_by(Product.category)
        .all()
        if category
    ]


# =====================================================
# GET PRODUCT BY ID
# =====================================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.add(ProductView(
        product_id=product.id,
        user_id=current_user.id if current_user else None,
    ))
    db.commit()

    return add_rating_aggregates([product], db)[0]


# =====================================================
# GET PRODUCTS BY CATEGORY
# =====================================================

@router.get(
    "/category/{category}",
    response_model=list[ProductResponse]
)
def get_products_by_category(
    category: str,
    db: Session = Depends(get_db)
):

    products = db.query(Product).filter(
        Product.category == category,
        Product.is_active == True
    ).order_by(
        Product.popularity.desc()
    ).all()

    return add_rating_aggregates(products, db)