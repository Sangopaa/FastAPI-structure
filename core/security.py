import jwt
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from fastapi import HTTPException, status
from configurations.security import security_settings


def create_access_token(
    subject: str | Any, expires_delta: Optional[timedelta] = None
) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=security_settings.access_token_expire_minutes)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, security_settings.jwt_secret, algorithm=security_settings.algorithm
    )
    return encoded_jwt


def get_google_auth_url() -> str:
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={security_settings.google_client_id}"
        f"&redirect_uri={security_settings.google_redirect_uri}"
        "&scope=openid%20profile%20email"
        "&access_type=offline"
        "&prompt=consent"
    )
    return url


async def get_google_user_info(code: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        token_data = {
            "client_id": security_settings.google_client_id,
            "client_secret": security_settings.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": security_settings.google_redirect_uri,
        }
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data=token_data,
        )
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange token with Google: {token_response.text}",
            )

        token_json = token_response.json()
        access_token = token_json.get("access_token")

        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_info_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from Google",
            )

        return user_info_response.json()
