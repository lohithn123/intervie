"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import AsyncSessionLocal
from db import crud
from schemas import UserCreate, UserResponse, Token, LoginRequest
from auth.auth_utils import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    get_current_user
)
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if user exists
    existing_user = await crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await crud.get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = await crud.create_user(
        db,
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and receive access token."""
    # Try to find user by username or email
    user = await crud.get_user_by_username(db, form_data.username)
    if not user:
        user = await crud.get_user_by_email(db, form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role
    }
    access_token = create_access_token(access_token_data)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: dict = Depends(get_current_user)
):
    """Refresh access token using current token."""
    access_token_data = {
        "sub": str(current_user.id),
        "username": current_user.username,
        "role": current_user.role
    }
    access_token = create_access_token(access_token_data)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current user information."""
    return current_user

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (client should discard the token)."""
    # In a more sophisticated system, you might want to blacklist the token
    # For now, we just return a success message
    return {"message": "Successfully logged out"} 