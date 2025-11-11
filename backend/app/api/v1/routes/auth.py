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


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/signup", response_model=Token)
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

    access_token = auth_service.create_access_token(user_id=user.id)
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
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

    access_token = auth_service.create_access_token(user_id=user.id)
    return Token(access_token=access_token, token_type="bearer")
