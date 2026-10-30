from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, decode_access_token
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.auth import UserRegister

security_scheme = HTTPBearer(auto_error=False)

def register_user(db: Session, user_in: UserRegister) -> User:
    """
    Registers a new student user and creates their default profile.
    Checks for duplicate emails.
    """
    existing = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    # Hash password with bcrypt
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        email=user_in.email.lower(),
        password_hash=hashed_pwd,
        full_name=user_in.full_name,
        role=user_in.role or "student",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create associated student profile
    profile = StudentProfile(
        user_id=user.id,
        college_name=user_in.college_name or "Engineering College",
        degree=user_in.degree or "B.Tech",
        branch=user_in.branch or "CSE",
        cgpa=7.0,
        technical_skills=["Python", "SQL"],
        soft_skills=["Problem Solving", "Communication"],
        programming_languages=["Python"],
        interests=["Software Development"]
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return user

def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Validates user credentials. Raises 401 if invalid.
    """
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )
    return user

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to protect routes with JWT Bearer authentication.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account."
        )
    return user
