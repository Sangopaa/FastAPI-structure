from fastapi import Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from typing import Any

from core.custom_router import CustomRouter

from core.security import get_google_auth_url, get_google_user_info, create_access_token
from configurations.database import get_session

from models.accounts.user import User
from repositories.user import user_repository

from schemas.accounts.user import AuthRequest

router = CustomRouter()


# Custom Login


@router.post("/create-account", summary="Create Account")
async def create_account(
    data: AuthRequest,
    response: Response,
    session: Session = Depends(get_session),
):
    user = user_repository.get_by_email(session, data.email)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    user = User(email=data.email)
    user.set_password(password=data.password)
    user = user_repository.create(session, user)

    token = create_access_token(subject=str(user.id))

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )

    return {"message": "Successfully authenticated.", "user": user.model_dump()}


@router.post("/login", summary="Login Account")
async def login_account(
    email: str, password: str, response: Response, session=Depends(get_session)
):
    user = user_repository.get_by_email(session, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(subject=str(user.id))

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )

    return {"message": "Successfully authenticated.", "user": user.model_dump()}


# OAuth 2.0 Google


@router.get("/google/login", summary="Redirects to Google Auth")
async def login_google():
    """Redirects the user to Google login consent screen."""
    url = get_google_auth_url()
    return RedirectResponse(url)


@router.get("/google/callback", summary="Google OAuth Callback")
async def gogole_auth_callback(
    code: str, response: Response, session: Session = Depends(get_session)
) -> Any:
    """Handles Google OAuth callback, creates or fetches user, and sets HttpOnly cookie"""
    google_user = await get_google_user_info(code)

    email = google_user.get("email")
    google_id = google_user.get("id")
    name = google_user.get("name")
    picture = google_user.get("picture")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google",
        )

    user = user_repository.get_by_email(session, email)

    if not user:
        user = User(
            email=email, google_id=google_id, full_name=name, avatar_url=picture
        )
        user = user_repository.create(session, user)
    else:
        update_needed = False
        if not user.google_id:
            user.google_id = google_id
            update_needed = True
        if not user.avatar_url and picture:
            user.avatar_url = picture
            update_needed = True

        if update_needed:
            user_repository.create(session, user)

    token = create_access_token(subject=str(user.id))

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )

    return {"message": "Successfully authenticated.", "user": user.model_dump()}
