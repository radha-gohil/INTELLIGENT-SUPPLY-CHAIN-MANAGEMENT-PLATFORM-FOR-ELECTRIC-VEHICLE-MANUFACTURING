from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.models.user import User

from backend.app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserResponse
)

from backend.app.service.auth_service import (
    authenticate_user,
    create_access_token,
    get_current_user
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Authenticate user
    # --------------------------------------------------------

    user = authenticate_user(
        db=db,
        email=request.email,
        password=request.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # --------------------------------------------------------
    # Update last login time
    # --------------------------------------------------------

    user.last_login = datetime.utcnow()

    db.commit()
    db.refresh(user)

    # --------------------------------------------------------
    # Create JWT access token
    # --------------------------------------------------------

    access_token = create_access_token(
        user
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


# ============================================================
# CURRENT LOGGED-IN USER
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):

    return current_user