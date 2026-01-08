from datetime import datetime, timedelta
from jose import jwt
from api.models.token_models import TokenData
from api.config import SECRET_KEY, ALGORITHM, JWT_EXPIRATION_DELTA, fake_users_db

def authenticate_user(username: str, password: str):
    """Verifica si el usuario existe y la contraseña es correcta."""
    user = fake_users_db.get(username)

    if not user or user["password"] != password:
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Genera un token de acceso JWT."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or JWT_EXPIRATION_DELTA)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)