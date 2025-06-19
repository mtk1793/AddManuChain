# src/db/models/product.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    JSON,
    Table,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .user import Base
from .certification import Certification  # Add this import


# Association table for product-certification relationship
product_certification = Table(
    "product_certification",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("certification_id", Integer, ForeignKey("certifications.id"), primary_key=True),
    extend_existing=True,  # Add this parameter
)


class Product(Base):
    """Model for manufactured products"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    product_code = Column(String(50), unique=True)
    price = Column(Float)
    status = Column(String(20), default="Active")  # Active, Discontinued, In Development

    # Foreign keys
    designer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=True)
    oem_id = Column(Integer, ForeignKey("oems.id"), nullable=True)
    blueprint_id = Column(Integer, ForeignKey("blueprints.id"), nullable=True)  # New foreign key

    # Product details
    specifications = Column(JSON, nullable=True)
    dimensions = Column(String(100))
    weight = Column(Float)
    materials_used = Column(Text)
    assembly_instructions = Column(Text)
    image_url = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships - add both designer and creator
    designer = relationship("User", foreign_keys=[designer_id], back_populates="designed_products")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_products")
    category = relationship("ProductCategory", back_populates="products")
    oem = relationship("OEM", back_populates="products")
    certifications = relationship(
        "Certification",
        secondary=product_certification,
        back_populates="products"
    )
    blueprint = relationship("Blueprint", back_populates="products")  # New relationship
    quality_tests = relationship("QualityTest", back_populates="product")  # Add the missing relationship to QualityTest

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"


class ProductCategory(Base):
    """Model for product categories"""

    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<ProductCategory(id={self.id}, name='{self.name}')>"


class OEM(Base):
    """Original Equipment Manufacturer model for product sourcing and manufacturing"""

    __tablename__ = "oems"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    # Add these missing fields
    status = Column(String(20), default="Active")  # This field is missing
    contact_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    location = Column(String(100))
    partnership_type = Column(String(50))
    contract_start_date = Column(DateTime)
    contract_end_date = Column(DateTime)
    description = Column(Text)
    website = Column(String(200))
    logo_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="oem")

    def __repr__(self):
        return f"<OEM(id={self.id}, name='{self.name}')>"
