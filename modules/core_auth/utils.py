from passlib.context import CryptContext
from passlib.hash import argon2
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from core.config import settings
import secrets

# Password hashing context using Argon2ID
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__rounds=2,
    argon2__memory_cost=65536,
    argon2__parallelism=1
)


def hash_password(password: str) -> str:
    """Hash a password using Argon2ID"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Verify token type
        if payload.get("type") != token_type:
            return None

        return payload
    except JWTError:
        return None


def generate_mfa_secret() -> str:
    """Generate a random MFA secret"""
    return secrets.token_urlsafe(32)


def is_strong_password(password: str) -> tuple[bool, str]:
    """
    Check if password meets strength requirements

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - No common passwords
    - No sequential characters
    """
    # Common weak passwords to block
    COMMON_PASSWORDS = [
        "password", "password123", "123456", "12345678", "qwerty", "abc123",
        "monkey", "letmein", "trustno1", "dragon", "baseball", "iloveyou",
        "master", "sunshine", "ashley", "bailey", "passw0rd", "shadow",
        "123123", "654321", "superman", "qazwsx", "michael", "football"
    ]

    # Minimum 8 characters
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    # Check for common passwords
    if password.lower() in COMMON_PASSWORDS:
        return False, "This password is too common. Please choose a unique password"

    # Character type requirements
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    if not has_upper:
        return False, "Password must contain at least one uppercase letter"
    if not has_lower:
        return False, "Password must contain at least one lowercase letter"
    if not has_digit:
        return False, "Password must contain at least one number"
    if not has_special:
        return False, "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"

    # Check for sequential characters (123, abc, etc.)
    sequential_patterns = [
        "012", "123", "234", "345", "456", "567", "678", "789", "890",
        "abc", "bcd", "cde", "def", "efg", "fgh", "ghi", "hij", "ijk",
        "jkl", "klm", "lmn", "mno", "nop", "opq", "pqr", "qrs", "rst",
        "stu", "tuv", "uvw", "vwx", "wxy", "xyz"
    ]

    password_lower = password.lower()
    for pattern in sequential_patterns:
        if pattern in password_lower or pattern[::-1] in password_lower:
            return False, "Password cannot contain sequential characters (like '123' or 'abc')"

    return True, "Password is strong"
