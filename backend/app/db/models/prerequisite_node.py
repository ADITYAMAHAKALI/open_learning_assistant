# app/db/models/prerequisite_node.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class PrerequisiteNode(Base):
    __tablename__ = "prerequisite_nodes"

    id = Column(Integer, primary_key=True)
    session_id = Column(
        Integer,
        ForeignKey("learning_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id = Column(Integer, ForeignKey("prerequisite_nodes.id"), nullable=True)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    wikipedia_summary = Column(Text, nullable=True)
    wikipedia_url = Column(String(1024), nullable=True)

    session = relationship("LearningSession", back_populates="prerequisite_nodes")
    parent = relationship("PrerequisiteNode", remote_side=[id], backref="children")
