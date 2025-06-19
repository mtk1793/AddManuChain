# src/db/models/material.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Float,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
import datetime

from .user import Base
# Import instead of defining again
from .certification import Certification, material_certification_association

class MaterialCategory(Base):
    """Material category classification"""
    __tablename__ = "material_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    materials = relationship("Material", back_populates="category")

    def __repr__(self):
        return f"<MaterialCategory(id={self.id}, name='{self.name}')>"


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    type = Column(String(50), nullable=False)  # Polymer, Metal, Ceramic, etc.
    # Add this for compatibility with material_service.py
    material_type = Column(String(50))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    category_id = Column(Integer, ForeignKey("material_categories.id"))
    stock_quantity = Column(Float, default=0)
    # For compatibility with both naming conventions
    current_stock = Column(Float, default=0)
    unit = Column(String(20), default="kg")
    unit_of_measure = Column(String(20), default="kg")
    price_per_unit = Column(Float)
    cost_per_unit = Column(Float)
    min_stock_level = Column(Float)
    reorder_level = Column(Float, default=10.0)
    location = Column(String(100))
    storage_location = Column(String(100))
    expiration_date = Column(DateTime)
    manager_id = Column(Integer, ForeignKey("users.id"))
    status = Column(
        String(20), default="Available"
    )  # Available, Low, Out of Stock, Expired
    is_active = Column(Boolean, default=True)
    properties = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    supplier = relationship("Supplier", back_populates="materials")
    category = relationship("MaterialCategory", back_populates="materials")
    manager = relationship("User", back_populates="materials_managed")
    # Reference the imported class and correct the M2M relationship
    certifications = relationship(
        "Certification",
        secondary=material_certification_association,
        back_populates="materials"
    )
    material_certifications = relationship("MaterialCertification", back_populates="material")
    stock_adjustments = relationship("StockAdjustment", back_populates="material")
    print_jobs = relationship("PrintJob", back_populates="material")

    def __repr__(self):
        return f"<Material(id={self.id}, name='{self.name}', quantity={self.stock_quantity}{self.unit})>"


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(255))
    website = Column(String(255))
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    materials = relationship("Material", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}')>"


class StockAdjustment(Base):
    """Material stock adjustment model."""
    __tablename__ = "stock_adjustments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    adjustment_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    quantity = Column(Float, nullable=False)  # Positive for additions, negative for removals
    adjustment_type = Column(String(50), nullable=False)  # Purchase, Usage, Write-off, etc.
    notes = Column(Text)
    unit_cost = Column(Float)  # Cost per unit for this adjustment
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    material = relationship("Material", back_populates="stock_adjustments")

    def __repr__(self):
        return f"<StockAdjustment(id={self.id}, material_id={self.material_id}, quantity={self.quantity})>"


class MaterialCertification(Base):
    """Material certification model."""
    __tablename__ = "material_certifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    certification_type = Column(String(100), nullable=False)  # FDA, ISO, etc.
    issuer = Column(String(100), nullable=False)
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    certification_number = Column(String(100))
    notes = Column(Text)
    document_url = Column(String(255))
    status = Column(String(20), default="Active")  # Active, Expired, Revoked
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    material = relationship("Material", back_populates="material_certifications")

    def __repr__(self):
        return f"<MaterialCertification(id={self.id}, material_id={self.material_id}, type='{self.certification_type}')>"
