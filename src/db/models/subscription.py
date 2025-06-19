# src/db/models/subscription.py
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


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_name = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    price = Column(Float, nullable=False)
    status = Column(String(20), default="Active")  # Active, Expired, Cancelled
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User")
    payments = relationship("Payment", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan='{self.plan_name}')>"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.datetime.utcnow)
    payment_method = Column(String(50))
    transaction_id = Column(String(100))
    status = Column(String(20), default="Completed")  # Completed, Failed, Refunded
    notes = Column(String(500))

    # Relationships
    subscription = relationship("Subscription", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, subscription_id={self.subscription_id}, amount={self.amount})>"
