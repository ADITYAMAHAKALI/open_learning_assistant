# app/services/auth_service.py
from abc import ABC, abstractmethod
from typing import Optional, Dict

from app.db.models.user import User


class AuthService(ABC):
    @abstractmethod
    def create_user(self, email: str, password: str, name: str | None = None) -> User:
        raise NotImplementedError

    @abstractmethod
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def create_tokens(self, user_id: int) -> Dict[str, str]:
        """
        Return a dict with:
        {
          "access_token": str,
          "refresh_token": str,
          "token_type": "bearer"
        }
        """
        raise NotImplementedError

    @abstractmethod
    def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
        """
        Validate + rotate refresh token, return new access + refresh.
        """
        raise NotImplementedError

    @abstractmethod
    def revoke_refresh_token(self, refresh_token: str) -> None:
        """
        Revoke a refresh token (e.g. on logout).
        """
        raise NotImplementedError
