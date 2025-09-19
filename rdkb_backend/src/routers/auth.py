from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.database import get_db
from src.core.security import create_access_token, get_password_hash, verify_password
from src.dependencies.auth import get_current_user, require_admin
from src.models.models import User
from src.schemas.auth import Token
from src.schemas.common import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/login", response_model=Token, summary="Login and obtain JWT token", description="Authenticate using email and password")
# PUBLIC_INTERFACE
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    """Authenticate user and issue JWT token."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(subject=user.email, expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=UserOut, summary="Register new user", description="Admin-only endpoint to create a new user")
# PUBLIC_INTERFACE
def register(user_in: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> UserOut:
    """Create a new user (admin only)."""
    exists = db.query(User).filter(User.email == user_in.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_admin=user_in.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
    )


@router.get("/me", response_model=UserOut, summary="Get current user profile")
# PUBLIC_INTERFACE
def me(current=Depends(get_current_user)) -> UserOut:
    """Return the current authenticated user."""
    return UserOut(
        id=current.id,
        email=current.email,
        is_active=current.is_active,
        is_admin=current.is_admin,
        created_at=current.created_at,
    )
