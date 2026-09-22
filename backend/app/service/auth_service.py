import os

from datetime import datetime, timedelta, timezone

import jwt

from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from jwt import InvalidTokenError

from pwdlib import PasswordHash

from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.models.user import User


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

JWT_ACCESS_TOKEN_MINUTES = int(
    os.getenv(
        "JWT_ACCESS_TOKEN_MINUTES",
        "480"
    )
)


if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is not configured. "
        "Add JWT_SECRET_KEY to your .env file."
    )


# ============================================================
# PASSWORD HASHING
# ============================================================

password_hasher = PasswordHash.recommended()


# ============================================================
# BEARER AUTHENTICATION
# ============================================================

bearer_scheme = HTTPBearer()


# ============================================================
# HASH PASSWORD
# ============================================================

def hash_password(password: str) -> str:

    if not password:
        raise ValueError(
            "Password cannot be empty."
        )

    return password_hasher.hash(
        password
    )


# ============================================================
# VERIFY PASSWORD
# ============================================================

def verify_password(
    plain_password: str,
    password_hash: str
) -> bool:

    if not plain_password:
        return False

    if not password_hash:
        return False

    try:

        return password_hasher.verify(
            plain_password,
            password_hash
        )

    except Exception:

        return False


# ============================================================
# CREATE JWT ACCESS TOKEN
# ============================================================

def create_access_token(
    user: User
) -> str:

    now = datetime.now(
        timezone.utc
    )

    expires_at = now + timedelta(
        minutes=JWT_ACCESS_TOKEN_MINUTES
    )

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "iat": now,
        "exp": expires_at
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


# ============================================================
# AUTHENTICATE USER
# ============================================================

def authenticate_user(
    db: Session,
    email: str,
    password: str
):

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        return None

    if not user.is_active:
        return None

    password_valid = verify_password(
        password,
        user.password_hash
    )

    if not password_valid:
        return None

    return user


# ============================================================
# GET CURRENT LOGGED-IN USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(
        get_db
    )
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[
                JWT_ALGORITHM
            ]
        )

        user_id = payload.get(
            "sub"
        )

        if not user_id:
            raise credentials_exception

        user_id = int(
            user_id
        )

    except (
        InvalidTokenError,
        ValueError,
        TypeError
    ):

        raise credentials_exception


    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise credentials_exception

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )

    return user


# ============================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================

def require_roles(
    *allowed_roles
):

    def role_checker(
        current_user: User = Depends(
            get_current_user
        )
    ):

        if (
            current_user.role
            not in allowed_roles
        ):

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to perform this action."
                )
            )

        return current_user

    return role_checker