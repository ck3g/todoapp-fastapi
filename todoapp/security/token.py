from datetime import datetime, timedelta, timezone

from jose import jwt

from todoapp.models.user import User

# also can generate with `openssl rand -hex 32`
SECRET_KEY = "super-secret-key"  # TODO: move to .env
ALGORITHM = "HS256"


def encode_token(user: User, expires_delta=timedelta(minutes=30)) -> str:
    """Encodes JWT token"""
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {"sub": user.email, "user_id": user.id, "exp": expires}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    """Decodes JWT token"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
