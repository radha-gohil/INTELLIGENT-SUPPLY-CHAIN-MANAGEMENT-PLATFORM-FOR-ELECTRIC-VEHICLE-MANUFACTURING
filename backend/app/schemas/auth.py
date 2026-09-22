from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ============================================================
# LOGIN REQUEST
# ============================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


# ============================================================
# LOGIN RESPONSE
# ============================================================

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse