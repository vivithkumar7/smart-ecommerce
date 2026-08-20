import os

from dotenv import load_dotenv


load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "your-secret-key"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]
