# src/db/models/print_job.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .user import Base

class PrintJob(Base):
    """Model for tracking 3D printing jobs"""
    __tablename__ = "print_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="Pending")  # Pending, In Progress, Completed, Failed, Cancelled
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    
    # Stats and details
    file_path = Column(String(255))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    estimated_duration = Column(Float)  # In minutes
    actual_duration = Column(Float)     # In minutes
    material_used = Column(Float)       # In grams or ml
    success = Column(Boolean)
    failure_reason = Column(Text)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="print_jobs")
    device = relationship("Device", back_populates="print_jobs")
    material = relationship("Material", back_populates="print_jobs")
    
    def __repr__(self):
        return f"<PrintJob(id={self.id}, name='{self.name}', status='{self.status}')>"