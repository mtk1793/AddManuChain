# src/db/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
import datetime

from src.db.connection import Base  # IMPORT SHARED BASE

# Association tables for many-to-many relationships
user_certification = Table(
    "user_certification",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column(
        "certification_id", Integer, ForeignKey("certifications.id"), primary_key=True
    ),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Store hashed passwords only
    email = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    role = Column(
        String(20), nullable=False
    )  # Admin, Manager, Technician, End User, Certification Authority
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    certifications = relationship(
        "Certification", secondary="user_certification", back_populates="users"
    )
    devices_managed = relationship("Device", back_populates="manager")
    materials_managed = relationship("Material", back_populates="manager")
    designed_products = relationship(
        "Product", foreign_keys="Product.designer_id", back_populates="designer"
    )
    created_products = relationship(
        "Product", foreign_keys="Product.creator_id", back_populates="creator"
    )
    maintenance_tasks = relationship("MaintenanceRecord", back_populates="technician")
    print_jobs = relationship("PrintJob", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
