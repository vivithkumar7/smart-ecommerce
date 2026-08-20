from app.core.database import SessionLocal
from app.models.user import User
from app.models.cart import CartItem, Cart

db = SessionLocal()

# Clear dependent tables first (respect foreign keys)
cart_item_count = db.query(CartItem).delete()
print(f'Deleted {cart_item_count} cart items')

cart_count = db.query(Cart).delete()
print(f'Deleted {cart_count} carts')

# Now clear users
user_count = db.query(User).delete()
print(f'Deleted {user_count} users from the database')

db.commit()
db.close()
print('Database cleared successfully!')

