from datetime import timedelta

SECRET_KEY = "quantion2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

JWT_EXPIRATION_DELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

fake_users_db = {
    "quantion": {
        "username": "quantion",
        "password": "quantion2025"
    }
}

