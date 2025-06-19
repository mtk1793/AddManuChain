"""
Database models package initialization.
"""

# First, import Base
from .user import Base

# Import all models in the right order
from .user import User
from .device import Device, MaintenanceRecord
from .certification import Certification
from .material import (
    Material, 
    MaterialCategory, 
    MaterialCertification,
    StockAdjustment,
    Supplier
)
from .print_job import PrintJob
from .product import Product, ProductCategory, OEM, product_certification  # Added ProductCategory here
from .quality import QualityTest
from .blueprint import Blueprint, blueprint_certification

# Explicitly re-export all models for easy import
__all__ = [
    'Base', 
    'User',
    'Device', 
    'MaintenanceRecord',
    'Certification',
    'Material', 
    'MaterialCategory', 
    'MaterialCertification',
    'StockAdjustment',
    'Supplier',
    'PrintJob',
    'Product', 
    'ProductCategory',  # Added ProductCategory here
    'OEM',
    'product_certification',
    'QualityTest',
    'Blueprint',
    'blueprint_certification'
]

# Make sure all models are registered before configuring
from sqlalchemy.orm import configure_mappers
configure_mappers()

