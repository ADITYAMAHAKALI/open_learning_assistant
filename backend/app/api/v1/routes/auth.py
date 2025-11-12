# app/api/v1/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.services.auth_service import AuthService
from app.core.deps import get_auth_service

router = APIRouter()


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


@router.post("/signup", response_model=TokenPair)
def signup(
    payload: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = auth_service.create_user(
            email=payload.email,
            password=payload.password,
            name=payload.name,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    tokens = auth_service.create_tokens(user_id=user.id)
    return tokens


@router.post("/login", response_model=TokenPair)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    # We treat "username" as email
    user = auth_service.authenticate_user(
        email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = auth_service.create_tokens(user_id=user.id)
    return tokens


@router.post("/refresh", response_model=TokenPair)
def refresh_tokens(
    payload: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        tokens = auth_service.refresh_tokens(payload.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    auth_service.revoke_refresh_token(payload.refresh_token)
    return
