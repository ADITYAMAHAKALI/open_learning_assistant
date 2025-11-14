# app/db/models/learning_session_material.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class LearningSessionMaterial(Base):
    __tablename__ = "learning_session_materials"

    session_id = Column(
        Integer,
        ForeignKey("learning_sessions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    material_id = Column(
        Integer,
        ForeignKey("learning_materials.id", ondelete="CASCADE"),
        primary_key=True,
    )

    session = relationship("LearningSession", back_populates="material_links")
    material = relationship("LearningMaterial")
