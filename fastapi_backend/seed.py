from app.core.database import SessionLocal, engine, Base
from app.models.product import Product
from app.models.cart import Cart, CartItem
from datetime import datetime, timezone

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Product images served by the FastAPI backend
IMAGES = {
    'smartwatch': 'http://127.0.0.1:8000/assets/Smart-Watch.jpg',
    'laptop': 'http://127.0.0.1:8000/assets/Laptop.jpg',
    'mouse': 'http://127.0.0.1:8000/assets/Mouse.jpg',
    'keyboard': 'http://127.0.0.1:8000/assets/KeyBoard.jpg',
    'shoes': 'http://127.0.0.1:8000/assets/Shoes.jpg',
    'cable': 'http://127.0.0.1:8000/assets/USB-cable.jpg',
    'earbuds': 'http://127.0.0.1:8000/assets/Wireless Earbuds.jpg',
    'stand': 'http://127.0.0.1:8000/assets/Phone Stand.jpg',
    'webcam': 'http://127.0.0.1:8000/assets/Web-Cam.png',
}

# Sample products with color block placeholder images

products = [
    Product(
        name='Smart Watch',
        description='Fitness smart watch with heart rate monitor and GPS',
        category='Electronics',
        price=3999.00,
        popularity=4.9,
        stock=15,
        image_url=IMAGES['smartwatch'],
        is_active=True,
        created_at=datetime.now(timezone.utc)
    ),
    Product(
        name='Laptop Pro',
        description='High performance laptop with 16GB RAM and SSD storage',
        category='Electronics',
        price=999.99,
        popularity=4.8,
        stock=8,
        image_url=IMAGES['laptop'],
        is_active=True,
        created_at=datetime.now(timezone.utc)
    ),
    Product(
        name='Wireless Mouse',
        description='Bluetooth wireless mouse with ergonomic design',
        category='Electronics',
        price=799.00,
        popularity=4.8,
        stock=50,
        image_url=IMAGES['mouse'],
        is_active=True,
        created_at=datetime.now(timezone.utc)
    ),
    Product(
        name='Mechanical Keyboard',
        description='RGB Mechanical keyboard with Cherry MX switches',
        category='Electronics',
        price=149.99,
        popularity=4.7,
        stock=25,
        image_url=IMAGES['keyboard'],
        is_active=True,
        created_at=datetime.now(timezone.utc)
    ),
    Product(
        name='Running Shoes',
        description='Lightweight running shoes with cushioned sole',
        category='Sports',
        price=4999.00,
        popularity=4.6,
        stock=20,
        image_url=IMAGES['shoes'],
        is_active=True,
        created_at=datetime.now(timezone.utc)
    ),
    Product(
        name='USB-C Cable',
        description='High-speed USB-C charging and data cable (2m)',
        category='Accessories',
        price=399.00,
        popularity=4.5,
        stock=100,
        image_url=IMAGES['cable'],
        is_active=True,
        created_at=datetime.now(timezone.utc)
    ),
    Product(
        name='Wireless Earbuds',
        description='Noise-cancelling wireless earbuds with 8-hour battery',
        category='Electronics',
        price=5999.00,
        popularity=4.6,
        stock=30,
        image_url=IMAGES['earbuds'],
        is_active=True,
        created_at=datetime.now(timezone.utc)
    ),
    Product(
        name='Phone Stand',
        description='Adjustable phone stand for desk and table',
        category='Accessories',
        price=299.00,
        popularity=4.4,
        stock=40,
        image_url=IMAGES['stand'],
        is_active=True,
        created_at=datetime.now(timezone.utc)
    ),
    Product(
        name='Webcam HD',
        description='1080p HD webcam with built-in microphone',
        category='Electronics',
        price=2999.00,
        popularity=4.5,
        stock=18,
        image_url=IMAGES['webcam'],
        is_active=True,
        created_at=datetime.now(timezone.utc)
    ),
]

# Clear existing products and cart items (respect foreign keys)
db.query(CartItem).delete()  # Delete cart items first
db.query(Cart).delete()       # Delete carts
db.query(Product).delete()    # Then delete products
db.commit()

db.add_all(products)
db.commit()
print(f'Seeded {len(products)} products successfully!')

# Verify
all_products = db.query(Product).all()
for p in all_products:
    print(f'  ID: {p.id}, Name: {p.name}, Price: {p.price}')
db.close()
