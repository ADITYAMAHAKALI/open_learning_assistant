from jose import jwt
import pytest

from app.services_impl.auth_service_impl import AuthServiceImpl
from app.core.config import settings
from app.db.models.refresh_token import RefreshToken


@pytest.fixture()
def auth_service(db):
    return AuthServiceImpl(db=db)


def test_create_user_and_authenticate(auth_service, db):
    user = auth_service.create_user("alice@example.com", "secret123", name="Alice")
    assert user.id is not None
    assert user.email == "alice@example.com"

    auth_user = auth_service.authenticate_user("alice@example.com", "secret123")
    assert auth_user is not None
    assert auth_user.id == user.id

    bad_auth = auth_service.authenticate_user("alice@example.com", "wrong")
    assert bad_auth is None


def test_create_tokens_returns_access_and_refresh(auth_service, db):
    user = auth_service.create_user("bob@example.com", "secret123")
    tokens = auth_service.create_tokens(user_id=user.id)

    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    payload = jwt.decode(
        tokens["access_token"],
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert payload["sub"] == str(user.id)
    assert payload["type"] == "access"


def test_refresh_tokens_rotates_refresh_token(auth_service, db):
    user = auth_service.create_user("carol@example.com", "secret123")
    tokens = auth_service.create_tokens(user_id=user.id)

    old_refresh = tokens["refresh_token"]

    new_tokens = auth_service.refresh_tokens(old_refresh)
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] != old_refresh

    payload = jwt.decode(
        old_refresh,
        settings.REFRESH_TOKEN_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    old_jti = payload["jti"]

    rt = db.query(RefreshToken).filter_by(jti=old_jti).first()
    assert rt is not None
    assert rt.revoked is True
    assert rt.replaced_by_jti is not None


def test_refresh_tokens_with_revoked_token_fails(auth_service, db):
    user = auth_service.create_user("dave@example.com", "secret123")
    tokens = auth_service.create_tokens(user_id=user.id)
    refresh = tokens["refresh_token"]

    auth_service.revoke_refresh_token(refresh)

    with pytest.raises(ValueError) as exc:
        auth_service.refresh_tokens(refresh)

    assert "revoked" in str(exc.value).lower()


def test_revoke_refresh_token_on_invalid_token_is_noop(auth_service, db):
    # Should not raise
    auth_service.revoke_refresh_token("this-is-not-a-valid-jwt")
