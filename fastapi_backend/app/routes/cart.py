import os

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.cart import Cart, CartItem
from app.models.product import Product

from app.schemas.cart import (
    CartAddRequest,
    CartUpdateRequest,
    CartRemoveRequest,
    CartResponse,
    CartItemResponse
)

from app.dependencies.auth import get_current_user
from app.services.notifications import manager


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


TAX_RATE = float(
    os.getenv(
        "TAX_RATE",
        "0.18"
    )
)


# =====================================================
# GET OR CREATE USER CART
# =====================================================

def get_or_create_cart(
    db: Session,
    user_id: int
):

    cart = db.query(Cart).filter(
        Cart.user_id == user_id
    ).first()

    if not cart:

        cart = Cart(
            user_id=user_id
        )

        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


# =====================================================
# CALCULATE CART
# =====================================================

def calculate_cart(cart):

    items = []

    subtotal = 0.0

    for item in cart.items:

        item_total = (
            item.unit_price *
            item.quantity
        )

        subtotal += item_total

        items.append(
            CartItemResponse(
                product_id=item.product_id,

                product_name=item.product.name,

                quantity=item.quantity,

                unit_price=item.unit_price,

                item_total=round(
                    item_total,
                    2
                )
            )
        )

    tax = subtotal * TAX_RATE

    grand_total = subtotal + tax

    return CartResponse(

        cart_id=cart.id,

        items=items,

        subtotal=round(
            subtotal,
            2
        ),

        tax=round(
            tax,
            2
        ),

        grand_total=round(
            grand_total,
            2
        )
    )


# =====================================================
# ADD PRODUCT TO CART
# =====================================================

@router.post(
    "/add",
    response_model=CartResponse
)
async def add_to_cart(

    request: CartAddRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    if request.quantity <= 0:

        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    product = db.query(Product).filter(
        Product.id == request.product_id,
        Product.is_active == True
    ).first()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if product.stock <= 0:

        raise HTTPException(
            status_code=400,
            detail="Product is out of stock"
        )

    if request.quantity > product.stock:

        raise HTTPException(
            status_code=400,
            detail=f"Only {product.stock} items available"
        )

    cart = get_or_create_cart(
        db,
        current_user.id
    )

    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product.id
    ).first()

    if cart_item:

        new_quantity = (
            cart_item.quantity +
            request.quantity
        )

        if new_quantity > product.stock:

            raise HTTPException(
                status_code=400,
                detail="Requested quantity exceeds available stock"
            )

        cart_item.quantity = new_quantity

    else:

        cart_item = CartItem(

            cart_id=cart.id,

            product_id=product.id,

            quantity=request.quantity,

            unit_price=product.price
        )

        db.add(cart_item)

    # Reduce stock
    product.stock -= request.quantity

    db.commit()
    db.refresh(cart)
    await manager.publish(current_user.id, {"event": "cart_updated"})

    return calculate_cart(cart)


# =====================================================
# UPDATE CART QUANTITY
# =====================================================

@router.put(
    "/update",
    response_model=CartResponse
)
async def update_cart(

    request: CartUpdateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart:

        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == request.product_id
    ).first()

    if not cart_item:

        raise HTTPException(
            status_code=404,
            detail="Product not found in cart"
        )

    product = db.query(Product).filter(
        Product.id == request.product_id
    ).first()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    old_quantity = cart_item.quantity

    new_quantity = request.quantity

    if new_quantity <= 0:

        product.stock += old_quantity

        db.delete(cart_item)

    elif new_quantity > old_quantity:

        extra_quantity = (
            new_quantity -
            old_quantity
        )

        if extra_quantity > product.stock:

            raise HTTPException(
                status_code=400,
                detail="Not enough stock available"
            )

        product.stock -= extra_quantity

        cart_item.quantity = new_quantity

    else:

        returned_quantity = (
            old_quantity -
            new_quantity
        )

        product.stock += returned_quantity

        cart_item.quantity = new_quantity

    db.commit()
    db.refresh(cart)
    await manager.publish(current_user.id, {"event": "cart_updated"})

    return calculate_cart(cart)


# =====================================================
# REMOVE PRODUCT
# =====================================================

@router.delete(
    "/remove",
    response_model=CartResponse
)
async def remove_from_cart(

    request: CartRemoveRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart:

        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == request.product_id
    ).first()

    if not cart_item:

        raise HTTPException(
            status_code=404,
            detail="Product not found in cart"
        )

    product = db.query(Product).filter(
        Product.id == request.product_id
    ).first()

    # Return stock
    if product:

        product.stock += cart_item.quantity

    db.delete(cart_item)

    db.commit()
    db.refresh(cart)
    await manager.publish(current_user.id, {"event": "cart_updated"})

    return calculate_cart(cart)


# =====================================================
# VIEW CART
# =====================================================

@router.get(
    "",
    response_model=CartResponse
)
def get_cart(

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    cart = get_or_create_cart(
        db,
        current_user.id
    )

    return calculate_cart(cart)