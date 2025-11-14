# app/db/models/learning_session.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    objective = Column(String(1024), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="learning_sessions")
    material_links = relationship(
        "LearningSessionMaterial",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    prerequisite_nodes = relationship(
        "PrerequisiteNode",
        back_populates="session",
        cascade="all, delete-orphan",
    )
