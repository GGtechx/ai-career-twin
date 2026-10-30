from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.config import settings
from app.schemas.auth import UserRegister, UserLogin, Token, UserAuthResponse
from app.services.auth_service import register_user, authenticate_user, get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new student user and returns an active JWT access token.
    """
    user = register_user(db, user_in)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserAuthResponse.model_validate(user)
    )

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates student credentials and returns a JWT access token.
    """
    user = authenticate_user(db, login_in.email, login_in.password)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserAuthResponse.model_validate(user)
    )

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Client-side token disposal confirmation.
    """
    return {"message": "Successfully logged out. Client should discard token."}

@router.get("/me", response_model=UserAuthResponse)
def get_auth_me(current_user: User = Depends(get_current_user)):
    """
    Returns current authenticated user details.
    """
    return UserAuthResponse.model_validate(current_user)
