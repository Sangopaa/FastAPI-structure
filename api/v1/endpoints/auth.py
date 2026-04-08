from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from typing import Any

from core.security import get_google_auth_url, get_google_user_info, create_access_token
from configurations.database import get_session
from models.user import User

router = APIRouter()

@router.get("/login", summary="Redirects to Google Auth")
async def login_google():
    """Redirects the user to Google login consent screen."""
    url = get_google_auth_url()
    return RedirectResponse(url)

@router.get("/callback", summary="Google OAuth Callback")
async def auth_callback(code: str, response: Response, session: Session = Depends(get_session)) -> Any:
    """Handles Google OAuth callback, creates or fetches user, and sets HttpOnly cookie"""
    google_user = await get_google_user_info(code)
    
    email = google_user.get("email")
    google_id = google_user.get("id")
    name = google_user.get("name")
    picture = google_user.get("picture")
    
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not provided by Google")
        
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    
    if not user:
        user = User(
            email=email,
            google_id=google_id,
            full_name=name,
            avatar_url=picture
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        update_needed = False
        if not user.google_id:
            user.google_id = google_id
            update_needed = True
        if not user.avatar_url and picture:
            user.avatar_url = picture
            update_needed = True
            
        if update_needed:
            session.add(user)
            session.commit()
    
    token = create_access_token(subject=str(user.id))

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 24 * 7 * 60
    )
    
    return {"message": "Successfully authenticated.", "user": user.model_dump()}
