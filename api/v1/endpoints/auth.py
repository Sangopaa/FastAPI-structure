from fastapi import Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from core.custom_router import CustomRouter
from core.security import get_google_auth_url
from configurations.database import get_session
from schemas.accounts.user import AuthRequest
from services.auth import auth_service

router = CustomRouter()


def set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )


# Custom Login


@router.post("/create-account", summary="Create Account")
async def create_account(
    data: AuthRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    user_data, token = await auth_service.create_account(session, data)
    set_auth_cookie(response, token)
    return {"message": "Successfully authenticated.", "user": user_data}


@router.post("/login", summary="Login Account")
async def login_account(
    email: str,
    password: str,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    user_data, token = await auth_service.login_account(session, email, password)
    set_auth_cookie(response, token)
    return {"message": "Successfully authenticated.", "user": user_data}


# OAuth 2.0 Google


@router.get("/google/login", summary="Redirects to Google Auth")
async def login_google():
    """Redirects the user to Google login consent screen."""
    url = get_google_auth_url()
    return RedirectResponse(url)


@router.get("/google/callback", summary="Google OAuth Callback")
async def gogole_auth_callback(
    code: str, response: Response, session: AsyncSession = Depends(get_session)
) -> Any:
    """Handles Google OAuth callback, creates or fetches user, and sets HttpOnly cookie"""
    user_data, token = await auth_service.handle_google_auth(session, code)
    set_auth_cookie(response, token)
    return {"message": "Successfully authenticated.", "user": user_data}
