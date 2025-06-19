# src/db/models/quality.py
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


class QualityTest(Base):
    __tablename__ = "quality_tests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    test_type = Column(String(50), nullable=False)  # Visual, Mechanical, Chemical, etc.
    tester_id = Column(Integer, ForeignKey("users.id"))
    test_date = Column(DateTime, default=datetime.datetime.utcnow)
    result = Column(String(20))  # Pass, Fail, Pending
    measurements = Column(String(500))
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="quality_tests")
    tester = relationship("User")

    def __repr__(self):
        return f"<QualityTest(id={self.id}, product_id={self.product_id}, result='{self.result}')>"
