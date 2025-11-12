# app/db/models/refresh_token.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # JWT "jti" claim – unique ID for this refresh token
    jti = Column(String(64), unique=True, index=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    revoked = Column(Boolean, default=False, nullable=False)

    # For token rotation
    parent_jti = Column(String(64), nullable=True)
    replaced_by_jti = Column(String(64), nullable=True)

    user = relationship("User", backref="refresh_tokens")
