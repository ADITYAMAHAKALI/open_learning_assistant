# app/services_impl/auth_service_impl.py
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.user import User
from app.services.auth_service import AuthService


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthServiceImpl(AuthService):
    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_user(self, email: str, password: str, name: str | None = None) -> User:
        existing = self._get_user_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")

        user = User(
            email=email,
            hashed_password=self._hash_password(password),
            name=name,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self._get_user_by_email(email)
        if not user:
            return None
        if not self._verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, user_id: int) -> str:
        to_encode = {
            "sub": str(user_id),
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return encoded_jwt
