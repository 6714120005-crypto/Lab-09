"""
User routes.
Protected endpoints for user profile management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User
from schemas import UserResponse, UserUpdate, MessageResponse
from auth import get_current_active_user, get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the profile of the currently authenticated user.
    Requires valid access token in Authorization header.
    """
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
async def update_current_user_profile(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update the profile of the currently authenticated user.
    Requires valid access token in Authorization header.

    - **username**: New username (optional, must be unique)
    """
    # Check if new username is taken
    if user_update.username and user_update.username != current_user.username:
        existing = await db.execute(
            select(User).where(User.username == user_update.username)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )
        current_user.username = user_update.username

    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Deactivate current user account",
)
async def deactivate_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Deactivate the current user's account.
    This is a soft delete - the account can be reactivated later.
    Requires valid access token in Authorization header.
    """
    current_user.is_active = False
    await db.flush()

    return MessageResponse(
        message="Account deactivated successfully",
        detail="Your account has been deactivated. Contact support to reactivate.",
    )
