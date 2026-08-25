from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, engine

from app.models import (
    User,
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    Notification,
)

from app.routes.product import router as product_router
from app.routes.cart import router as cart_router
from app.routes.auth import router as auth_router
from app.routes.checkout import router as checkout_router
from app.routes.notifications import router as notifications_router


# Create tables
Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Smart E-Commerce API",
    description="Product catalog, cart, checkout, order, and Stripe payment API",
    version="1.0.0"
)

assets_dir = Path(__file__).resolve().parent / "assets"
app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# =====================================================
# ROUTES
# =====================================================

app.include_router(
    auth_router
)

app.include_router(
    product_router
)

app.include_router(
    cart_router
)

app.include_router(
    checkout_router
)

app.include_router(
    notifications_router
)


@app.get("/")
def root():

    return {
        "message": "Smart E-Commerce API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }