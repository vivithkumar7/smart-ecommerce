from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


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

    return query.all()


# =====================================================
# GET PRODUCT BY ID
# =====================================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,
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

    return product


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

    return products