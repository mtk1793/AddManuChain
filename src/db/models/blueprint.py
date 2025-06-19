# src/db/models/blueprint.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

from .user import Base

# Association tables for many-to-many relationships
blueprint_certification = Table(
    "blueprint_certification",
    Base.metadata,
    Column("blueprint_id", Integer, ForeignKey("blueprints.id"), primary_key=True),
    Column(
        "certification_id", Integer, ForeignKey("certifications.id"), primary_key=True
    ),
)


class Blueprint(Base):
    __tablename__ = "blueprints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # STL, OBJ, etc.
    version = Column(String(20), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"))
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(20), default="Draft")  # Draft, Review, Approved, Deprecated
    notes = Column(String(500))

    # Relationships
    creator = relationship("User")
    certifications = relationship(
        "Certification", 
        secondary="blueprint_certification", 
        back_populates="blueprints"
    )
    products = relationship("Product", back_populates="blueprint")

    def __repr__(self):
        return (
            f"<Blueprint(id={self.id}, name='{self.name}', version='{self.version}')>"
        )
