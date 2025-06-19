# src/db/models/certification.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,  # Add Date type
    ForeignKey,
    Table,
    Text,  # Add Text type
    JSON,  # Add JSON type
)
from sqlalchemy.orm import relationship
import datetime
from .user import Base
from .blueprint import blueprint_certification  # Add this import at the top of your certification.py file

# Association table for many-to-many relationships
material_certification_association = Table(
    "material_certification_association",
    Base.metadata,
    Column("material_id", Integer, ForeignKey("materials.id"), primary_key=True),
    Column(
        "certification_id", Integer, ForeignKey("certifications.id"), primary_key=True
    ),
)

# Association table for certification-user relationship
user_certification_association = Table(
    "user_certification_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("certification_id", Integer, ForeignKey("certifications.id"), primary_key=True),
)

class Certification(Base):
    __tablename__ = "certifications"
    __table_args__ = {'extend_existing': True}  # Add this line to fix the error

    id = Column(Integer, primary_key=True)
    cert_number = Column(String(100), nullable=False)
    cert_type = Column(String(50), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True)
    issuing_authority = Column(String(100), nullable=False)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    status = Column(String(50), default="Active", nullable=False)
    requirements = Column(Text, nullable=True)
    documents = Column(JSON, nullable=True)  # Store document info as JSON
    
    # Add this missing column
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    # Relationships
    materials = relationship(
        "Material", secondary=material_certification_association, back_populates="certifications"
    )
    # Add the missing users relationship
    users = relationship(
        "User", secondary=user_certification_association, back_populates="certifications"
    )
    # If you have a direct creator relationship
    created_by = relationship("User", foreign_keys=[created_by_id])
    products = relationship("Product", secondary="product_certification", back_populates="certifications")
    # Add the missing relationship to Blueprint
    blueprints = relationship(
        "Blueprint", 
        secondary=blueprint_certification,  # Use the imported table
        back_populates="certifications"
    )

    def __repr__(self):
        return f"<Certification(id={self.id}, name='{self.name}')>"
