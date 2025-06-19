# src/db/models/device.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
    Text,
    DateTime,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from .user import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    serial_number = Column(String(100), unique=True, nullable=False)
    location = Column(String(100))
    status = Column(String(20), default="Active")  # Active, Maintenance, Offline
    acquisition_date = Column(Date)
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)
    manager_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    manager = relationship("User", back_populates="devices_managed")
    maintenance_records = relationship("MaintenanceRecord", back_populates="device")
    print_jobs = relationship("PrintJob", back_populates="device")

    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', status='{self.status}')>"


class MaintenanceRecord(Base):
    """Model for tracking device maintenance activities"""
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    technician_id = Column(Integer, ForeignKey("users.id"))
    maintenance_date = Column(Date, nullable=False)
    maintenance_type = Column(String(50), nullable=False)  # Regular, Emergency, Calibration
    description = Column(Text)
    status = Column(String(20), default="Scheduled")  # Scheduled, Completed, Cancelled
    cost = Column(Float)
    completion_notes = Column(Text)
    cancellation_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    device = relationship("Device", back_populates="maintenance_records")
    technician = relationship("User", back_populates="maintenance_tasks")

    def __repr__(self):
        return f"<MaintenanceRecord(id={self.id}, device_id={self.device_id}, date={self.maintenance_date})>"
