from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")
    full_name: str = Field(..., min_length=2, max_length=150)
    role: Optional[str] = "student"
    college_name: Optional[str] = None
    degree: Optional[str] = "B.Tech"
    branch: Optional[str] = "CSE"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserAuthResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserAuthResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
