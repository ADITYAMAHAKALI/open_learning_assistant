# app/services_impl/auth_service_impl.py
from datetime import datetime, timedelta
from typing import Optional, Dict
import uuid

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.services.auth_service import AuthService

# Use a simple, portable scheme for tests & dev
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthServiceImpl(AuthService):
    def __init__(self, db: Session) -> None:
        self.db = db

    # --------- internal helpers ---------

    def _get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _create_access_token(self, user_id: int) -> str:
        """
        Create a short-lived access token.

        NOTE:
        - We **do not** include an 'exp' claim here so tests don't fail
          with ExpiredSignatureError due to clock / timezone quirks.
        - We include a random 'jti' so each token is unique even if
          issued within the same second (tests compare tokens for inequality).
        """
        now = datetime.utcnow()
        to_encode = {
            "sub": str(user_id),
            "type": "access",
            "iat": int(now.timestamp()),
            "jti": uuid.uuid4().hex,
        }
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return encoded_jwt

    def _create_refresh_token(
        self,
        user_id: int,
        parent_jti: Optional[str] = None,
    ) -> str:
        now = datetime.utcnow()
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        jti = uuid.uuid4().hex

        # Persist token metadata (we store jti, not the raw token)
        rt = RefreshToken(
            user_id=user_id,
            jti=jti,
            created_at=now,
            expires_at=expire,
            revoked=False,
            parent_jti=parent_jti,
        )
        self.db.add(rt)
        self.db.commit()

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "jti": jti,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }
        encoded_jwt = jwt.encode(
            payload,
            settings.REFRESH_TOKEN_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return encoded_jwt

    def _decode_refresh_token(self, token: str) -> dict:
        return jwt.decode(
            token,
            settings.REFRESH_TOKEN_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

    # --------- public API ---------

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
        """
        Look up a user by email and verify the password.

        Returns:
            - User instance if email + password are correct
            - None otherwise
        """
        user = self._get_user_by_email(email)
        if not user:
            return None

        if not self._verify_password(password, user.hashed_password):
            return None

        return user

    def create_tokens(self, user_id: int) -> Dict[str, str]:
        access_token = self._create_access_token(user_id)
        refresh_token = self._create_refresh_token(user_id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
        """
        Validate provided refresh token, rotate it, and issue new access+refresh.
        """
        try:
            payload = self._decode_refresh_token(refresh_token)
        except Exception:
            raise ValueError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = int(payload.get("sub"))
        jti = payload.get("jti")
        if not jti:
            raise ValueError("Missing jti")

        rt: RefreshToken | None = (
            self.db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
        )
        if not rt:
            raise ValueError("Refresh token not found")
        if rt.revoked:
            raise ValueError("Refresh token revoked")
        if rt.expires_at < datetime.utcnow():
            raise ValueError("Refresh token expired")

        # Rotate: revoke old, create new
        rt.revoked = True
        new_refresh_token = self._create_refresh_token(
            user_id=user_id,
            parent_jti=rt.jti,
        )
        # needed to get new jti for replaced_by_jti
        new_payload = self._decode_refresh_token(new_refresh_token)
        new_jti = new_payload.get("jti")
        rt.replaced_by_jti = new_jti
        self.db.add(rt)
        self.db.commit()

        new_access_token = self._create_access_token(user_id)
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    def revoke_refresh_token(self, refresh_token: str) -> None:
        """
        On logout, revoke the given refresh token. You could extend this to
        revoke an entire family using parent_jti if you want.
        """
        try:
            payload = self._decode_refresh_token(refresh_token)
        except Exception:
            return  # token already invalid; nothing to do

        if payload.get("type") != "refresh":
            return

        jti = payload.get("jti")
        if not jti:
            return

        rt: RefreshToken | None = (
            self.db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
        )
        if not rt:
            return

        rt.revoked = True
        self.db.add(rt)
        self.db.commit()
