from src.db.models.user import User, user_certification
from src.db.models.device import Device, MaintenanceRecord
from src.db.models.material import Material, Supplier, MaterialCertification
from src.db.models.product import Product, OEM, product_certification  # Remove PrintJob from here
from src.db.models.blueprint import Blueprint, blueprint_certification
from src.db.models.quality import QualityTest
from src.db.models.certification import Certification
from src.db.models.subscription import Subscription, Payment
from src.db.models.print_job import PrintJob  # This is the correct import
