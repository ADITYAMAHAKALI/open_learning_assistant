# app/services/auth_service.py
from abc import ABC, abstractmethod
from typing import Optional

from app.db.models.user import User


class AuthService(ABC):
    @abstractmethod
    def create_user(self, email: str, password: str, name: str | None = None) -> User:
        raise NotImplementedError

    @abstractmethod
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def create_access_token(self, user_id: int) -> str:
        raise NotImplementedError
