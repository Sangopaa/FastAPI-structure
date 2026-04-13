from fastapi import HTTPException, status
from sqlmodel import Session

from core.security import create_access_token, get_google_user_info
from models.accounts.user import User
from repositories.accounts.user import user_repository
from schemas.accounts.user import AuthRequest


class AuthService:
    def __init__(self):
        self.user_repository = user_repository

    def create_account(self, session: Session, data: AuthRequest) -> tuple[dict, str]:
        user = self.user_repository.get_by_email(session, data.email)

        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        user = User(email=data.email)
        user.set_password(password=data.password)
        user = self.user_repository.create(session, user)

        token = create_access_token(subject=str(user.id))
        return user.model_dump(), token

    def login_account(
        self, session: Session, email: str, password: str
    ) -> tuple[dict, str]:
        user = self.user_repository.get_by_email(session, email)

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
        return user.model_dump(), token

    async def handle_google_auth(self, session: Session, code: str) -> tuple[dict, str]:
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

        user = self.user_repository.get_by_email(session, email)

        if not user:
            user = User(
                email=email, google_id=google_id, full_name=name, avatar_url=picture
            )
            user = self.user_repository.create(session, user)
        else:
            update_needed = False
            if not user.google_id:
                user.google_id = google_id
                update_needed = True
            if not user.avatar_url and picture:
                user.avatar_url = picture
                update_needed = True

            if update_needed:
                self.user_repository.update(session, user, user)

        token = create_access_token(subject=str(user.id))
        return user.model_dump(), token


auth_service = AuthService()
