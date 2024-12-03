from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


def hash_password(password) -> str:
    """Hashes the password"""
    return pwd_context.hash(password)


def verify_password(password, hashed_password) -> bool:
    """Return False when password verifycation fails"""
    try:
        return pwd_context.verify(password, hashed_password)
    except ValueError:
        return False
